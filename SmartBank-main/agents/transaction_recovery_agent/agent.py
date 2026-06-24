"""
SmartFinance AI — Failed Transaction Recovery Agent

Detects failed transactions where money was deducted but payment failed,
communicates with merchant APIs, and generates refund requests automatically.

Technology: UiPath Agent Builder, LLM Agent, LangChain/CrewAI
"""

from __future__ import annotations

import json
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

logger = logging.getLogger("smartbank.agents.transaction_recovery")


class TransactionStatus(str, Enum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    PENDING = "PENDING"
    REFUNDED = "REFUNDED"
    DISPUTED = "DISPUTED"


class RecoveryMethod(str, Enum):
    AUTO_REFUND = "AUTO_REFUND"
    MERCHANT_DISPUTE = "MERCHANT_DISPUTE"
    HUMAN_REVIEW = "HUMAN_REVIEW"
    CHARGEBACK = "CHARGEBACK"


@dataclass
class FailedTransaction:
    id: str
    customer_id: str
    amount: float
    currency: str
    merchant: str
    merchant_ref: str
    transaction_date: str
    failure_reason: str
    amount_deducted: bool
    current_status: str


@dataclass
class RecoveryResult:
    customer_id: str
    failed_transactions: list[dict]
    total_recoverable: float
    recovery_method: str
    auto_recoverable: bool
    requires_human_review: bool
    recommended_action: str
    analysis_summary: str
    confidence: float
    timestamp: str


class TransactionRecoveryAgent:
    def __init__(self, config: Optional[dict[str, Any]] = None):
        self.config = config or {}
        self.auto_recovery_threshold = float(self.config.get("auto_recovery_threshold", 5000.0))
        self.merchant_api_enabled = self.config.get("merchant_api_enabled", False)

    def analyze(
        self,
        customer_id: str,
        failed_transactions: list[FailedTransaction],
    ) -> RecoveryResult:
        recoverable: list[dict] = []
        total_recoverable = 0.0
        auto_ok = True
        needs_human = False
        method = RecoveryMethod.AUTO_REFUND

        for txn in failed_transactions:
            if not txn.amount_deducted:
                continue

            entry = {
                "txn_id": txn.id,
                "merchant": txn.merchant,
                "amount": txn.amount,
                "date": txn.transaction_date,
                "reason": txn.failure_reason,
                "status": txn.current_status,
            }
            recoverable.append(entry)
            total_recoverable += txn.amount

            if txn.amount > self.auto_recovery_threshold:
                auto_ok = False
                needs_human = True
                method = RecoveryMethod.HUMAN_REVIEW
            elif self.merchant_api_enabled:
                method = RecoveryMethod.AUTO_REFUND
            else:
                method = RecoveryMethod.MERCHANT_DISPUTE

        if recoverable:
            summary = (
                f"Found {len(recoverable)} failed transaction(s) totaling Rs.{total_recoverable:.0f}. "
                f"Amount was deducted but payment failed."
            )
            if auto_ok:
                action = f"Auto-generating refund requests for {len(recoverable)} transaction(s) via merchant APIs."
            else:
                action = (
                    f"Transaction(s) exceed auto-recovery threshold. "
                    f"Creating dispute cases for human review."
                )
        else:
            summary = "No recoverable failed transactions found."
            action = "Continue monitoring."

        return RecoveryResult(
            customer_id=customer_id,
            failed_transactions=recoverable,
            total_recoverable=round(total_recoverable, 2),
            recovery_method=method.value,
            auto_recoverable=auto_ok,
            requires_human_review=needs_human,
            recommended_action=action,
            analysis_summary=summary,
            confidence=0.90 if recoverable else 0.99,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
