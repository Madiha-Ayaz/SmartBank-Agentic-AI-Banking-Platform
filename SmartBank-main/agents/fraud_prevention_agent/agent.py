"""
SmartFinance AI — Fraud Prevention Agent

Analyzes transaction behavior, detects unauthorized transactions,
calculates fraud risk scores, and recommends actions.

Technology: UiPath Agent Builder, LLM Agent, LangChain/CrewAI
"""

from __future__ import annotations

import json
import logging
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any, Optional

logger = logging.getLogger("smartbank.agents.fraud_prevention")


class FraudRiskLevel(str):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass
class Transaction:
    id: str
    amount: float
    currency: str
    merchant: str
    category: str
    timestamp: str
    location: str
    is_international: bool
    is_online: bool


@dataclass
class FraudAnalysisResult:
    customer_id: str
    risk_score: float
    risk_level: str
    suspicious_indicators: list[str]
    recommended_action: str
    requires_human_review: bool
    analysis_summary: str
    confidence: float
    timestamp: str


class FraudPreventionAgent:
    INDICATORS = {
        "unusual_location": 25,
        "high_amount": 20,
        "rapid_succession": 20,
        "international_txn": 15,
        "new_merchant": 10,
        "amount_deviation": 30,
        "off_hours": 10,
        "card_not_present": 5,
    }

    def __init__(self, config: Optional[dict[str, Any]] = None):
        self.config = config or {}
        self.high_risk_threshold = float(self.config.get("high_risk_threshold", 50.0))
        self.llm_api_key = self.config.get("llm_api_key", "")

    def analyze(
        self,
        customer_id: str,
        transaction: Transaction,
        historical_transactions: list[Transaction],
        customer_risk_score: float = 0.0,
    ) -> FraudAnalysisResult:
        indicators = []
        score = 0.0

        score += self._check_unusual_location(transaction, historical_transactions)
        score += self._check_high_amount(transaction, historical_transactions)
        score += self._check_international(transaction)
        score += self._check_new_merchant(transaction, historical_transactions)
        score += self._check_off_hours(transaction)
        score += customer_risk_score * 0.2

        if score > 0:
            indicators.append(f"Fraud indicators detected: score={score:.1f}")

        if score >= self.INDICATORS["unusual_location"]:
            indicators.append("Unusual transaction location compared to history")
        if transaction.is_international:
            indicators.append("International transaction detected")
        if transaction.amount > 100000:
            indicators.append("High-value transaction exceeds threshold")

        risk_level = self._determine_risk_level(score)
        requires_review = score >= self.high_risk_threshold

        if requires_review:
            action = "Temporarily block transaction and request customer verification"
        elif score >= 30:
            action = "Flag for review and send customer alert"
        else:
            action = "Approve automatically - low risk"

        return FraudAnalysisResult(
            customer_id=customer_id,
            risk_score=round(score, 2),
            risk_level=risk_level,
            suspicious_indicators=indicators,
            recommended_action=action,
            requires_human_review=requires_review,
            analysis_summary=f"Transaction {transaction.id}: {risk_level} risk ({score:.1f}/100). {action}",
            confidence=min(0.95, 0.6 + score / 200),
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

    def _check_unusual_location(self, txn: Transaction, history: list[Transaction]) -> float:
        if not history:
            return 0.0
        locations = {h.location for h in history[-20:]}
        if txn.location not in locations:
            return self.INDICATORS["unusual_location"]
        return 0.0

    def _check_high_amount(self, txn: Transaction, history: list[Transaction]) -> float:
        if not history:
            return 0.0
        avg_amount = sum(h.amount for h in history[-20:]) / max(len(history[-20:]), 1)
        if avg_amount > 0 and txn.amount > avg_amount * 3:
            return self.INDICATORS["amount_deviation"]
        return 0.0

    def _check_international(self, txn: Transaction) -> float:
        if txn.is_international:
            return self.INDICATORS["international_txn"]
        return 0.0

    def _check_new_merchant(self, txn: Transaction, history: list[Transaction]) -> float:
        if not history:
            return self.INDICATORS["new_merchant"]
        merchants = {h.merchant for h in history[-30:]}
        if txn.merchant not in merchants:
            return self.INDICATORS["new_merchant"]
        return 0.0

    def _check_off_hours(self, txn: Transaction) -> float:
        try:
            hour = int(txn.timestamp.split("T")[1].split(":")[0])
            if hour < 6 or hour > 23:
                return self.INDICATORS["off_hours"]
        except (IndexError, ValueError):
            pass
        return 0.0

    def _determine_risk_level(self, score: float) -> str:
        if score >= 70:
            return FraudRiskLevel.CRITICAL
        elif score >= 50:
            return FraudRiskLevel.HIGH
        elif score >= 25:
            return FraudRiskLevel.MEDIUM
        return FraudRiskLevel.LOW
