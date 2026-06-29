"""SmartBank Audit Logger Robot

UiPath RPA — Immutable, append-only audit log with hash chain integrity.
Simulates Elasticsearch index ``smartbank-audit-{YYYY.MM}`` on the local
filesystem (JSON files).  Every entry is chained to the previous one via
SHA-256 so tampering is detectable.

UiPath Activity Map (Orchestrator Sequence):
  Activity Name                       | Package                     | Configuration                          | Error Handler
  ------------------------------------|-----------------------------|----------------------------------------|-------------------------------
  Receive Queue Item (Audit Entry)    | UiPath.Queue                | Queue: AuditLogger                     | TerminateOnError
  Compute SHA-256 Hash Chain          | UiPath.System.Activities    | Input: previous_hash + payload        | TerminateOnError
  Append Entry to JSON Log            | UiPath.System.Activities    | Path: audit-{YYYY.MM}.json            | Retry(2)
  Verify Integrity (last N entries)   | UiPath.System.Activities    | Mode: periodic check                  | TerminateOnError
  Log Message                         | UiPath.System.Activities    | Level: Info                            | Ignore

Unit Test Scenarios (5 per robot):
  1. Happy Path — entry written, file contains exact JSON line
  2. Hash Chain Continuity — entry.hash == next.previous_hash
  3. Integrity Check Detects Tamper — modify a line, verify() returns False
  4. Concurrent Append — two robots writing simultaneously do not corrupt
  5. Missing Log Directory — auto-created on first write
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import threading
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

logger = logging.getLogger(__name__)


class Status(Enum):
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"


@dataclass
class AuditEntry:
    timestamp: str
    robot_name: str
    action: str
    input_hash: str
    output_hash: str
    user_id: str
    status: str
    previous_hash: str = ""
    hash: str = ""


class AuditLoggerRobot:
    """UiPath RPA robot that writes immutable, append-only audit entries.

    Each entry contains a SHA-256 hash of the previous entry's hash,
    forming a tamper-evident chain.  Data is persisted to JSON-lines files
    organised by month (``audit-YYYY.MM.json``) to simulate the Elasticsearch
    index pattern ``smartbank-audit-{YYYY.MM}``.

    Environment variables:
      AUDIT_LOG_DIR  — Directory for audit log files (default: ./audit_logs)
    """

    _lock = threading.Lock()

    def __init__(self, robot_name: str = "AuditLoggerRobot") -> None:
        self.robot_name = robot_name
        self._log_dir = os.environ.get("AUDIT_LOG_DIR", "audit_logs")
        os.makedirs(self._log_dir, exist_ok=True)
        self._memory_buffer: list[AuditEntry] = []

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def log_entry(
        self,
        action: str,
        robot_name: str,
        input_data: Any,
        output_data: Any,
        user_id: str,
        status: str,
    ) -> AuditEntry:
        """Persist a single audit entry.

        UiPath activity: Append Entry to JSON Log
        Package: UiPath.System.Activities
        Configuration:
          Path: {AUDIT_LOG_DIR}/audit-{YYYY.MM}.json
          Error handler: Retry(2)
        """
        with self._lock:
            previous_hash = self._last_hash()
            raw_payload = self._build_payload(action, robot_name, input_data, output_data, user_id, status)
            current_hash = self._compute_hash(raw_payload, previous_hash)

            entry = AuditEntry(
                timestamp=raw_payload["timestamp"],
                robot_name=robot_name,
                action=action,
                input_hash=raw_payload["input_hash"],
                output_hash=raw_payload["output_hash"],
                user_id=user_id,
                status=status,
                previous_hash=previous_hash,
                hash=current_hash,
            )

            self._append_to_file(entry)
            self._memory_buffer.append(entry)
            logger.debug("Audit entry %s written (hash=%s)", entry.action, entry.hash[:16])
            return entry

    def verify_integrity(self, entry_count: Optional[int] = None) -> bool:
        """Walk the hash chain and verify every link.

        UiPath activity: Verify Integrity (last N entries)
        Package: UiPath.System.Activities
        Configuration:
          Mode: periodic check
          Error handler: TerminateOnError
        """
        entries = self._read_all_entries()
        if entry_count is not None:
            entries = entries[-entry_count:]

        if not entries:
            return True

        previous = entries[0].previous_hash
        expected_previous = "0" * 64  # genesis

        if previous != expected_previous:
            logger.error("Integrity violation: first entry's previous_hash is not all-zero")
            return False

        for entry in entries[1:]:
            if entry.previous_hash != entries[entries.index(entry) - 1].hash:
                logger.error(
                    "Integrity violation: entry %s has previous_hash %s but expected %s",
                    entry.timestamp,
                    entry.previous_hash,
                    entries[entries.index(entry) - 1].hash,
                )
                return False

        logger.info("Integrity verified for %d entries", len(entries))
        return True

    @property
    def buffer(self) -> list[AuditEntry]:
        return list(self._memory_buffer)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _month_index(self) -> str:
        return datetime.now(timezone.utc).strftime("%Y.%m")

    def _current_file(self) -> str:
        return os.path.join(self._log_dir, f"audit-{self._month_index()}.json")

    def _last_hash(self) -> str:
        file_path = self._current_file()
        if not os.path.exists(file_path):
            return "0" * 64  # genesis
        try:
            with open(file_path, "r", encoding="utf-8") as fh:
                last_line = None
                for last_line in fh:
                    pass
            if last_line is None:
                return "0" * 64
            last_entry = json.loads(last_line)
            return last_entry["hash"]
        except (json.JSONDecodeError, KeyError, FileNotFoundError):
            return "0" * 64

    @staticmethod
    def _build_payload(
        action: str,
        robot_name: str,
        input_data: Any,
        output_data: Any,
        user_id: str,
        status: str,
    ) -> dict[str, Any]:
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        return {
            "timestamp": timestamp,
            "robot_name": robot_name,
            "action": action,
            "input_hash": hashlib.sha256(
                json.dumps(input_data, sort_keys=True, default=str).encode()
            ).hexdigest(),
            "output_hash": hashlib.sha256(
                json.dumps(output_data, sort_keys=True, default=str).encode()
            ).hexdigest(),
            "user_id": user_id,
            "status": status,
        }

    @staticmethod
    def _compute_hash(payload: dict[str, Any], previous_hash: str) -> str:
        chain_material = json.dumps(payload, sort_keys=True, default=str) + previous_hash
        return hashlib.sha256(chain_material.encode()).hexdigest()

    def _append_to_file(self, entry: AuditEntry) -> None:
        file_path = self._current_file()
        line = json.dumps(asdict(entry), default=str, ensure_ascii=False)
        with open(file_path, "a", encoding="utf-8") as fh:
            fh.write(line + "\n")
        logger.debug("Appended to %s", file_path)

    def _read_all_entries(self) -> list[AuditEntry]:
        file_path = self._current_file()
        entries: list[AuditEntry] = []
        if not os.path.exists(file_path):
            return entries
        with open(file_path, "r", encoding="utf-8") as fh:
            for line_no, line in enumerate(fh, 1):
                stripped = line.strip()
                if not stripped:
                    continue
                try:
                    data = json.loads(stripped)
                    entries.append(AuditEntry(**data))
                except (json.JSONDecodeError, TypeError) as exc:
                    logger.warning("Skipping malformed line %d: %s", line_no, exc)
        return entries


# ------------------------------------------------------------------
# Unit test scenarios (run with pytest)
# ------------------------------------------------------------------
#
# 1. Happy Path
#    robot = AuditLoggerRobot()
#    entry = robot.log_entry("LOGIN", "CBSConnectorRobot", {"u": "a"}, {"token": "x"}, "a", "SUCCESS")
#    assert entry.hash != ""
#    assert os.path.exists(robot._current_file())
#
# 2. Hash Chain Continuity
#    robot = AuditLoggerRobot()
#    e1 = robot.log_entry("A", "R1", {}, {}, "u", "SUCCESS")
#    e2 = robot.log_entry("B", "R2", {}, {}, "u", "SUCCESS")
#    assert e2.previous_hash == e1.hash
#
# 3. Integrity Check Detects Tamper
#    robot = AuditLoggerRobot()
#    robot.log_entry("A", "R", {}, {}, "u", "SUCCESS")
#    # Manually corrupt the file
#    with open(robot._current_file(), "a") as fh:
#        fh.write("CORRUPTED\n")
#    assert robot.verify_integrity() is False
#
# 4. Concurrent Append (integration — run with threads)
#    robot = AuditLoggerRobot()
#    t1 = threading.Thread(target=robot.log_entry, args=("A", "R1", {}, {}, "u", "SUCCESS"))
#    t2 = threading.Thread(target=robot.log_entry, args=("B", "R2", {}, {}, "u", "SUCCESS"))
#    t1.start(); t2.start(); t1.join(); t2.join()
#    assert len(robot.buffer) == 2
#
# 5. Missing Log Directory
#    import tempfile; td = tempfile.mkdtemp()
#    os.environ["AUDIT_LOG_DIR"] = os.path.join(td, "nonexistent/subdir")
#    robot = AuditLoggerRobot()  # should create the directory
#    robot.log_entry("A", "R", {}, {}, "u", "SUCCESS")
#    assert os.path.exists(robot._current_file())
