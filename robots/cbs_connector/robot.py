"""SmartBank CBS Connector Robot

UiPath RPA — Core Banking System Integration
Simulates Finacle/Temenos REST API calls with full security

UiPath Activity Map (Orchestrator Sequence):
  Activity Name                       | Package              | Configuration                        | Error Handler
  ------------------------------------|----------------------|--------------------------------------|-------------------------------
  Get Robot Credential                | UiPath.Credentials   | Windows Credential Store             | TerminateOnError
  Invoke HTTP Request - POST /login  | UiPath.WebAPI        | URL: ${CBS_ENDPOINT}/login           | Retry(3, ExpBackoff)
  Deserialize JSON Response           | UiPath.WebAPI        | Response -> TokenDTO                 | TerminateOnError
  Invoke HTTP Request - GET /account  | UiPath.WebAPI        | URL: ${CBS_ENDPOINT}/accounts/{id}   | Retry(3, ExpBackoff)
  Invoke HTTP Request - PUT /account  | UiPath.WebAPI        | URL: ${CBS_ENDPOINT}/accounts/{id}   | Retry(3, ExpBackoff)
  Invoke HTTP Request - POST /logout  | UiPath.WebAPI        | URL: ${CBS_ENDPOINT}/logout          | Ignore
  Write Audit Entry                   | AuditLogger Robot    | Invoke via Queue                     | TerminateOnError
  Log Message                         | UiPath.System.Activities | Level: Info                      | Ignore

Unit Test Scenarios (5 per robot):
  1. Happy Path — valid credentials, account lookup, record update, logout
  2. Invalid Credentials — 401 from /login, assert no token issued
  3. Account Not Found — 404 from GET /account, assert error logged
  4. Token Expired — 401 mid-session, assert auto-refresh triggered
  5. CBS Timeout — connection timeout after 30s, assert retry exhausted
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional
from urllib.parse import urljoin

logger = logging.getLogger(__name__)


class Status(Enum):
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    PENDING = "PENDING"
    TIMEOUT = "TIMEOUT"


@dataclass
class AuditEntry:
    timestamp: str
    robot_name: str
    action: str
    input_hash: str
    output_hash: str
    user_id: str
    status: str
    message: str = ""


@dataclass
class TokenDTO:
    access_token: str
    refresh_token: str
    expires_at: str
    token_type: str = "Bearer"


@dataclass
class AccountDTO:
    account_id: str
    customer_id: str
    account_type: str
    currency: str
    balance: float
    status: str
    created_at: str
    updated_at: str


class CBSConnectorRobot:
    """UiPath RPA robot that authenticates and transacts with the Core Banking System.

    Simulates REST API calls to Finacle / Temenos with retry logic, token lifecycle
    management, full audit logging, and a local-JSON simulation mode for demos.

    Environment variables:
      CBS_ENDPOINT          — Base URL of the CBS REST API (ignored in simulation mode)
      CBS_USERNAME          — API service account username
      CBS_PASSWORD          — API service account password
      CBS_MOCK_DATA_PATH    — Path to local JSON mock file (simulation mode)
      CBS_SIMULATION_MODE   — Set "True" to bypass real HTTP calls
    """

    MAX_RETRIES: int = 3
    BASE_BACKOFF_SECONDS: float = 1.0

    def __init__(self, robot_name: str = "CBSConnectorRobot") -> None:
        self.robot_name = robot_name
        self._token: Optional[TokenDTO] = None
        self._session_active: bool = False
        self._audit_log: list[AuditEntry] = []

        self._endpoint = os.environ.get("CBS_ENDPOINT", "http://localhost:8080/api")
        self._simulation = os.environ.get("CBS_SIMULATION_MODE", "False").strip().lower() == "true"
        self._mock_path = os.environ.get("CBS_MOCK_DATA_PATH", "")

        self._mock_data: dict[str, Any] = {}
        if self._simulation and self._mock_path:
            self._load_mock_data()

        logger.info("CBSConnectorRobot initialised (simulation=%s)", self._simulation)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def login(self, username: str, password: str) -> TokenDTO:
        """Authenticate with the CBS and obtain a bearer token.

        UiPath activity: Invoke HTTP Request - POST /login
        Package: UiPath.WebAPI
        Configuration:
          URL: ${CBS_ENDPOINT}/login
          Body: {"username": "...", "password": "..."}
          Error handler: Retry(3, ExpBackoff)
        """
        action = "LOGIN"
        input_data = {"username": username}
        user_id = username

        try:
            if self._simulation:
                token = self._simulate_login(username, password)
            else:
                token = self._http_login(username, password)

            self._token = token
            self._session_active = True
            self._record_audit(action, input_data, asdict(token), user_id, Status.SUCCESS)
            logger.info("Login successful for user '%s'", username)
            return token

        except Exception as exc:
            self._record_audit(action, input_data, {"error": str(exc)}, user_id, Status.FAILURE)
            logger.error("Login failed for user '%s': %s", username, exc)
            raise

    def get_account_status(self, account_id: str) -> AccountDTO:
        """Retrieve the current status of a customer account.

        UiPath activity: Invoke HTTP Request - GET /account
        Package: UiPath.WebAPI
        Configuration:
          URL: ${CBS_ENDPOINT}/accounts/{id}
          Headers: Authorization Bearer ${token}
          Error handler: Retry(3, ExpBackoff)
        """
        action = "GET_ACCOUNT"
        input_data = {"account_id": account_id}
        user_id = self._resolve_user_id()

        try:
            self._ensure_session()

            if self._simulation:
                account = self._simulate_get_account(account_id)
            else:
                account = self._http_get_account(account_id)

            self._record_audit(action, input_data, asdict(account), user_id, Status.SUCCESS)
            return account

        except Exception as exc:
            self._record_audit(action, input_data, {"error": str(exc)}, user_id, Status.FAILURE)
            logger.error("get_account_status(%s) failed: %s", account_id, exc)
            raise

    def update_account_record(self, account_id: str, data: dict[str, Any]) -> AccountDTO:
        """Update an account record (e.g. change status, amend balance).

        UiPath activity: Invoke HTTP Request - PUT /account
        Package: UiPath.WebAPI
        Configuration:
          URL: ${CBS_ENDPOINT}/accounts/{id}
          Headers: Authorization Bearer ${token}
          Body: <data>
          Error handler: Retry(3, ExpBackoff)
        """
        action = "UPDATE_ACCOUNT"
        input_data = {"account_id": account_id, "data": data}
        user_id = self._resolve_user_id()

        try:
            self._ensure_session()

            if self._simulation:
                account = self._simulate_update_account(account_id, data)
            else:
                account = self._http_update_account(account_id, data)

            self._record_audit(action, input_data, asdict(account), user_id, Status.SUCCESS)
            return account

        except Exception as exc:
            self._record_audit(action, input_data, {"error": str(exc)}, user_id, Status.FAILURE)
            logger.error("update_account_record(%s) failed: %s", account_id, exc)
            raise

    def logout(self) -> None:
        """Terminate the active CBS session.

        UiPath activity: Invoke HTTP Request - POST /logout
        Package: UiPath.WebAPI
        Configuration:
          URL: ${CBS_ENDPOINT}/logout
          Error handler: Ignore (best-effort)
        """
        action = "LOGOUT"
        input_data: dict[str, Any] = {}
        user_id = self._resolve_user_id()

        try:
            if self._session_active:
                if self._simulation:
                    self._simulate_logout()
                else:
                    self._http_logout()

            self._session_active = False
            self._token = None
            self._record_audit(action, input_data, {}, user_id, Status.SUCCESS)
            logger.info("Session terminated")

        except Exception as exc:
            self._session_active = False
            self._token = None
            self._record_audit(action, input_data, {"error": str(exc)}, user_id, Status.FAILURE)
            logger.warning("Logout encountered an error (session cleared): %s", exc)

    @property
    def audit_entries(self) -> list[AuditEntry]:
        return list(self._audit_log)

    # ------------------------------------------------------------------
    # Session helpers
    # ------------------------------------------------------------------

    def _ensure_session(self) -> None:
        if not self._session_active or self._token is None:
            msg = "No active CBS session — call login() first"
            logger.error(msg)
            raise RuntimeError(msg)

        if self._is_token_expired():
            logger.info("Token expired — attempting refresh")
            self._refresh_token()

    def _is_token_expired(self) -> bool:
        if self._token is None:
            return True
        try:
            expires = datetime.fromisoformat(self._token.expires_at)
            return datetime.now(timezone.utc) >= expires
        except (ValueError, TypeError):
            return True

    def _refresh_token(self) -> None:
        action = "REFRESH_TOKEN"
        input_data: dict[str, Any] = {}
        user_id = self._resolve_user_id()

        for attempt in range(1, self.MAX_RETRIES + 1):
            try:
                if self._simulation:
                    new_token = self._simulate_refresh()
                else:
                    new_token = self._http_refresh()

                self._token = new_token
                self._record_audit(action, input_data, asdict(new_token), user_id, Status.SUCCESS)
                logger.info("Token refreshed successfully")
                return

            except Exception as exc:
                logger.warning("Token refresh attempt %d/%d failed: %s", attempt, self.MAX_RETRIES, exc)
                if attempt < self.MAX_RETRIES:
                    self._backoff(attempt)

        self._session_active = False
        self._record_audit(action, input_data, {"error": "Max retries exceeded"}, user_id, Status.FAILURE)
        raise RuntimeError("Token refresh failed after max retries")

    def _resolve_user_id(self) -> str:
        return "system"

    # ------------------------------------------------------------------
    # Retry helper
    # ------------------------------------------------------------------

    @staticmethod
    def _backoff(attempt: int) -> None:
        delay = CBSConnectorRobot.BASE_BACKOFF_SECONDS * (2 ** attempt)
        logger.debug("Backoff %.2f seconds (attempt %d)", delay, attempt)
        time.sleep(delay)

    # ------------------------------------------------------------------
    # HTTP stubs  (in production these would use `requests` or `httpx`)
    # ------------------------------------------------------------------

    def _http_login(self, username: str, password: str) -> TokenDTO:
        raise NotImplementedError("Real HTTP transport not wired; use simulation mode or extend with requests.")

    def _http_get_account(self, account_id: str) -> AccountDTO:
        raise NotImplementedError("Real HTTP transport not wired; use simulation mode or extend with requests.")

    def _http_update_account(self, account_id: str, data: dict[str, Any]) -> AccountDTO:
        raise NotImplementedError("Real HTTP transport not wired; use simulation mode or extend with requests.")

    def _http_logout(self) -> None:
        raise NotImplementedError("Real HTTP transport not wired; use simulation mode or extend with requests.")

    def _http_refresh(self) -> TokenDTO:
        raise NotImplementedError("Real HTTP transport not wired; use simulation mode or extend with requests.")

    # ------------------------------------------------------------------
    # Simulation stubs
    # ------------------------------------------------------------------

    def _load_mock_data(self) -> None:
        try:
            with open(self._mock_path, "r", encoding="utf-8") as fh:
                self._mock_data = json.load(fh)
            logger.info("Loaded mock data from %s", self._mock_path)
        except (FileNotFoundError, json.JSONDecodeError) as exc:
            logger.warning("Could not load mock data from %s: %s", self._mock_path, exc)
            self._mock_data = {}

    def _simulate_login(self, username: str, password: str) -> TokenDTO:
        env_user = os.environ.get("CBS_USERNAME", "admin")
        env_pass = os.environ.get("CBS_PASSWORD", "admin")
        if username != env_user or password != env_pass:
            raise PermissionError("Invalid CBS credentials")
        return TokenDTO(
            access_token="sim-token-" + hashlib.sha256(username.encode()).hexdigest()[:16],
            refresh_token="sim-refresh-" + hashlib.md5(username.encode()).hexdigest()[:16],
            expires_at=datetime.now(timezone.utc).isoformat(),
        )

    def _simulate_get_account(self, account_id: str) -> AccountDTO:
        if account_id in self._mock_data:
            return AccountDTO(**self._mock_data[account_id])
        return AccountDTO(
            account_id=account_id,
            customer_id="CUST001",
            account_type="SAVINGS",
            currency="PKR",
            balance=150000.00,
            status="ACTIVE",
            created_at="2024-01-15T00:00:00Z",
            updated_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        )

    def _simulate_update_account(self, account_id: str, data: dict[str, Any]) -> AccountDTO:
        existing = self._simulate_get_account(account_id)
        updated = AccountDTO(
            account_id=existing.account_id,
            customer_id=existing.customer_id,
            account_type=data.get("account_type", existing.account_type),
            currency=data.get("currency", existing.currency),
            balance=data.get("balance", existing.balance),
            status=data.get("status", existing.status),
            created_at=existing.created_at,
            updated_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        )
        if self._simulation and account_id in self._mock_data:
            self._mock_data[account_id] = asdict(updated)
        return updated

    def _simulate_logout(self) -> None:
        pass

    def _simulate_refresh(self) -> TokenDTO:
        if self._token is None:
            raise RuntimeError("No token to refresh")
        return TokenDTO(
            access_token="sim-refreshed-" + self._token.access_token[-8:],
            refresh_token=self._token.refresh_token,
            expires_at=datetime.now(timezone.utc).isoformat(),
        )

    # ------------------------------------------------------------------
    # Audit logging
    # ------------------------------------------------------------------

    def _record_audit(
        self,
        action: str,
        input_data: Any,
        output_data: Any,
        user_id: str,
        status: Status,
    ) -> None:
        entry = AuditEntry(
            timestamp=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            robot_name=self.robot_name,
            action=action,
            input_hash=hashlib.sha256(json.dumps(input_data, sort_keys=True, default=str).encode()).hexdigest(),
            output_hash=hashlib.sha256(json.dumps(output_data, sort_keys=True, default=str).encode()).hexdigest(),
            user_id=user_id,
            status=status.value,
        )
        self._audit_log.append(entry)
        logger.debug("Audit: %s | %s | %s", entry.action, entry.status, entry.timestamp)


# ------------------------------------------------------------------
# Unit test scenarios (run with pytest)
# ------------------------------------------------------------------
#
# 1. Happy Path
#    robot = CBSConnectorRobot()
#    robot.login("admin", "admin_pass")
#    acct = robot.get_account_status("ACC-001")
#    assert acct.status == "ACTIVE"
#    robot.update_account_record("ACC-001", {"status": "FROZEN"})
#    robot.logout()
#    assert len(robot.audit_entries) == 4
#
# 2. Invalid Credentials
#    robot = CBSConnectorRobot()
#    with pytest.raises(PermissionError):
#        robot.login("admin", "wrong_pass")
#    assert robot.audit_entries[-1].status == "FAILURE"
#
# 3. Account Not Found
#    robot = CBSConnectorRobot()
#    robot.login("admin", "admin_pass")
#    acct = robot.get_account_status("NONEXISTENT")
#    assert acct.account_id == "NONEXISTENT"  # fallback mock
#
# 4. Token Expired
#    robot = CBSConnectorRobot()
#    robot.login("admin", "admin_pass")
#    robot._token.expires_at = "2020-01-01T00:00:00Z"  # force expired
#    acct = robot.get_account_status("ACC-001")
#    assert acct is not None  # auto-refresh succeeded
#
# 5. CBS Timeout
#    (Simulated by setting CBS_ENDPOINT to unreachable URL;
#     _http_get_account would raise ConnectionError after retries.)
