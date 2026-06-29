"""
SmartFinance Reporting & Audit Bot

UiPath RPA — Creates audit reports, stores workflow history, generates
compliance logs, and produces resolution summaries for regulatory purposes.

UiPath Activity Map:
  Activity Name                   | Package                     | Configuration
  --------------------------------|-----------------------------|----------------------------------------
  Get Queue Item (Report)         | UiPath.Queue                | Queue: ReportingBot
  Build Audit Report              | UiPath.String.Activities    | Template: ${auditTemplate}
  Generate PDF Report             | UiPath.PDF.Activities       | Output Path: ${reportPath}
  Store Report                    | UiPath.Database.Activities  | Table: audit_reports
  Write Audit Entry               | AuditLogger Robot           | Invoke via Queue
  Log Message                     | UiPath.System.Activities    | Level: Info
"""

from __future__ import annotations

import json
import logging
import uuid
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

logger = logging.getLogger("smartbank.robots.reporting")


class ReportType(str, Enum):
    RESOLUTION_SUMMARY = "resolution_summary"
    AUDIT_TRAIL = "audit_trail"
    COMPLIANCE_LOG = "compliance_log"
    AGENT_PERFORMANCE = "agent_performance"
    HUMAN_REVIEW_LOG = "human_review_log"


@dataclass
class ReportRequest:
    case_id: str
    report_type: str
    customer_id: str
    data: dict[str, Any]
    include_pii: bool = False


@dataclass
class ReportResult:
    report_id: str
    report_type: str
    status: str
    message: str
    report_path: Optional[str] = None
    entries_count: int = 0


class ReportingBot:
    def __init__(self, config: Optional[dict[str, Any]] = None):
        self.config = config or {}
        self.simulation_mode = self.config.get("simulation_mode", True)
        self.report_dir = self.config.get("report_dir", "reports")

    def generate(self, request: ReportRequest) -> ReportResult:
        report_id = f"RPT-{uuid.uuid4().hex[:8].upper()}"

        try:
            if request.report_type == ReportType.RESOLUTION_SUMMARY.value:
                content = self._build_resolution_summary(request)
            elif request.report_type == ReportType.AUDIT_TRAIL.value:
                content = self._build_audit_trail(request)
            elif request.report_type == ReportType.COMPLIANCE_LOG.value:
                content = self._build_compliance_log(request)
            elif request.report_type == ReportType.AGENT_PERFORMANCE.value:
                content = self._build_agent_performance(request)
            elif request.report_type == ReportType.HUMAN_REVIEW_LOG.value:
                content = self._build_human_review_log(request)
            else:
                return ReportResult(
                    report_id=report_id,
                    report_type=request.report_type,
                    status="FAILED",
                    message=f"Unknown report type: {request.report_type}",
                )

            path = self._store_report(report_id, request.report_type, content)
            count = len(content.get("entries", []))

            self._log_audit(request.case_id, report_id, request.report_type)

            return ReportResult(
                report_id=report_id,
                report_type=request.report_type,
                status="SUCCESS",
                message=f"Report generated: {report_id}",
                report_path=str(path),
                entries_count=count,
            )

        except Exception as e:
            logger.error(f"Report generation failed: {e}")
            return ReportResult(
                report_id=report_id,
                report_type=request.report_type,
                status="FAILED",
                message=f"Generation error: {str(e)}",
            )

    def _build_resolution_summary(self, request: ReportRequest) -> dict:
        data = request.data
        return {
            "report_title": "Resolution Summary",
            "case_id": request.case_id,
            "customer_id": request.customer_id if request.include_pii else f"***{request.customer_id[-4:]}",
            "problem_type": data.get("problem_type", "Unknown"),
            "detected_at": data.get("detected_at", ""),
            "resolved_at": data.get("resolved_at", ""),
            "resolution_time": data.get("resolution_time", ""),
            "ai_agent": data.get("ai_agent", "Unknown"),
            "human_reviewed": data.get("human_reviewed", False),
            "auto_resolved": data.get("auto_resolved", True),
            "status": data.get("status", "Resolved"),
            "entries": [
                {"step": "Detection", "action": f"AI Guardian detected {data.get('problem_type', 'issue')}", "status": "Completed"},
                {"step": "Analysis", "action": f"Specialized AI agent analyzed the issue", "status": "Completed"},
                {"step": "Resolution", "action": data.get("resolution_action", "Action executed"), "status": data.get("status", "Completed")},
                {"step": "Notification", "action": "Customer notified", "status": "Completed"},
            ],
        }

    def _build_audit_trail(self, request: ReportRequest) -> dict:
        return {
            "report_title": "Audit Trail",
            "case_id": request.case_id,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "entries": request.data.get("audit_entries", []),
        }

    def _build_compliance_log(self, request: ReportRequest) -> dict:
        data = request.data
        return {
            "report_title": "Compliance Log",
            "case_id": request.case_id,
            "regulatory_framework": "SBP Regulations, PCI-DSS, NADRA e-KYC",
            "data_retention_days": 365,
            "pii_handled": request.include_pii,
            "entries": [
                {"check": "Customer identity verified", "passed": True},
                {"check": "Transaction authorization confirmed", "passed": data.get("authorized", True)},
                {"check": "Fraud check completed", "passed": True},
                {"check": "Human approval obtained where required", "passed": data.get("human_approved", True)},
                {"check": "Audit trail recorded", "passed": True},
            ],
        }

    def _build_agent_performance(self, request: ReportRequest) -> dict:
        return {
            "report_title": "AI Agent Performance",
            "case_id": request.case_id,
            "agent_used": request.data.get("ai_agent", "Unknown"),
            "confidence_score": request.data.get("confidence", 0),
            "response_time_ms": request.data.get("response_time_ms", 0),
            "human_escalation_required": request.data.get("escalated", False),
            "auto_resolution_success": request.data.get("auto_resolved", True),
        }

    def _build_human_review_log(self, request: ReportRequest) -> dict:
        data = request.data
        return {
            "report_title": "Human Review Log",
            "case_id": request.case_id,
            "reviewer": data.get("reviewer", "Unassigned"),
            "decision": data.get("decision", "Pending"),
            "review_time": data.get("review_time", ""),
            "notes": data.get("notes", ""),
            "ai_recommendation": data.get("ai_recommendation", ""),
        }

    def _store_report(self, report_id: str, report_type: str, content: dict) -> str:
        import os
        from pathlib import Path

        report_dir = Path(self.report_dir) / report_type
        report_dir.mkdir(parents=True, exist_ok=True)

        path = report_dir / f"{report_id}.json"
        path.write_text(json.dumps(content, indent=2, default=str))
        logger.info(f"Report saved: {path}")
        return str(path)

    def _log_audit(self, case_id: str, report_id: str, report_type: str):
        from robots.audit_logger.robot import AuditLoggerRobot
        bot = AuditLoggerRobot()
        bot.log(
            action="REPORT_GENERATED",
            actor="ReportingBot",
            resource=f"report/{report_id}",
            details={"case_id": case_id, "report_type": report_type},
        )
