"""
SmartFinance AI Financial Guardian — Monitoring Agent

Continuously monitors customer financial behavior, detects anomalies,
predicts risks, and triggers specialized resolution workflows.

Technology: UiPath Agent Builder, LLM Agent, LangChain
"""

from __future__ import annotations

import enum
import json
import logging
import random
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any, Optional

logger = logging.getLogger("smartbank.agents.financial_monitoring")


class ProblemType(str, enum.Enum):
    FRAUD = "FRAUD"
    BILL = "BILL"
    RECOVERY = "RECOVERY"
    COACH = "COACH"
    NONE = "NONE"


class Severity(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass
class CustomerFinancialProfile:
    customer_id: str
    customer_name: str
    account_balance: float
    monthly_income: float
    monthly_expenses: float
    transaction_count_30d: int
    unusual_transactions_30d: int
    failed_payments_30d: int
    fraud_alerts_30d: int
    risk_score: float
    savings_rate: float
    bill_payment_reliability: float
    spending_categories: dict[str, float] = field(default_factory=dict)
    upcoming_bills: list[dict] = field(default_factory=list)
    recent_transactions: list[dict] = field(default_factory=list)


@dataclass
class MonitoringResult:
    customer_id: str
    timestamp: str
    problem_detected: bool
    problem_type: Optional[str]
    problem_severity: Optional[str]
    analysis_summary: str
    risk_score: float
    confidence: float
    recommendation: str
    raw_analysis: dict[str, Any] = field(default_factory=dict)


class FinancialMonitoringAgent:
    def __init__(self, config: Optional[dict[str, Any]] = None):
        self.config = config or {}
        self.problem_threshold = float(self.config.get("problem_threshold", 0.6))
        self.llm_api_key = self.config.get("llm_api_key", "")
        self.llm_model = self.config.get("llm_model", "openai/gpt-4o-mini")

    def analyze(self, profile: CustomerFinancialProfile) -> MonitoringResult:
        profile_summary = self._summarize_profile(profile)
        llm_analysis = self._call_llm(profile_summary)
        parsed = self._parse_llm_response(llm_analysis, profile)

        return MonitoringResult(
            customer_id=profile.customer_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            problem_detected=parsed["problem_detected"],
            problem_type=parsed["problem_type"],
            problem_severity=parsed["problem_severity"],
            analysis_summary=parsed["summary"],
            risk_score=parsed["risk_score"],
            confidence=parsed["confidence"],
            recommendation=parsed["recommendation"],
            raw_analysis=parsed,
        )

    def _summarize_profile(self, profile: CustomerFinancialProfile) -> str:
        return json.dumps(asdict(profile), indent=2, default=str)

    def _call_llm(self, profile_json: str) -> str:
        if self.llm_api_key:
            try:
                import requests
                resp = requests.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.llm_api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": self.llm_model,
                        "messages": [
                            {
                                "role": "system",
                                "content": (
                                    "You are SmartFinance AI Financial Guardian Agent. "
                                    "Analyze the customer financial profile and determine: "
                                    "1) Is there a financial problem? "
                                    "2) What type? (FRAUD, BILL, RECOVERY, COACH) "
                                    "3) Severity? (LOW, MEDIUM, HIGH, CRITICAL) "
                                    "4) Risk score (0-100) "
                                    "5) Confidence (0-1) "
                                    "6) Recommendation. "
                                    "Respond in JSON format with keys: "
                                    "problem_detected, problem_type, problem_severity, "
                                    "risk_score, confidence, summary, recommendation"
                                ),
                            },
                            {"role": "user", "content": profile_json},
                        ],
                    },
                    timeout=30,
                )
                return resp.json()["choices"][0]["message"]["content"]
            except Exception as e:
                logger.warning(f"LLM call failed: {e}, using fallback analysis")

        return self._local_analysis(profile_json)

    def _local_analysis(self, profile_json: str) -> str:
        data = json.loads(profile_json)
        balance = data.get("account_balance", 0)
        unusual = data.get("unusual_transactions_30d", 0)
        failed = data.get("failed_payments_30d", 0)
        fraud_alerts = data.get("fraud_alerts_30d", 0)
        expenses = data.get("monthly_expenses", 0)
        income = data.get("monthly_income", 0)

        problems = []
        severity = "LOW"

        if fraud_alerts > 0 or unusual > 3:
            problems.append("FRAUD")
            severity = "HIGH"

        if balance < 1000 and expenses > 0:
            problems.append("BILL")
            if len(problems) == 1:
                severity = "MEDIUM"

        if failed > 0:
            problems.append("RECOVERY")
            if severity == "LOW":
                severity = "MEDIUM"

        if income > 0 and expenses > income * 0.8:
            problems.append("COACH")
            if severity == "LOW":
                severity = "LOW"

        problem_detected = len(problems) > 0
        problem_type = problems[0] if problems else "NONE"
        risk_score = min(100, (unusual * 10 + failed * 15 + fraud_alerts * 25 + (1 if not problem_detected else 0)))

        return json.dumps({
            "problem_detected": problem_detected,
            "problem_type": problem_type,
            "problem_severity": severity,
            "risk_score": risk_score,
            "confidence": 0.85 if problem_detected else 0.95,
            "summary": f"Detected {len(problems)} potential issues: {', '.join(problems)}" if problems else "Customer financial behavior is normal.",
            "recommendation": (
                f"Trigger {problem_type} resolution workflow" if problem_detected
                else "Continue monitoring - no action needed"
            ),
        })

    def _parse_llm_response(self, response: str, profile: CustomerFinancialProfile) -> dict:
        try:
            cleaned = response.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.split("\n", 1)[1]
                cleaned = cleaned.rsplit("\n", 1)[0]
                if cleaned.endswith("```"):
                    cleaned = cleaned[:-3]
            parsed = json.loads(cleaned)
            return {
                "problem_detected": bool(parsed.get("problem_detected", False)),
                "problem_type": str(parsed.get("problem_type", "NONE")),
                "problem_severity": str(parsed.get("problem_severity", "LOW")),
                "risk_score": float(parsed.get("risk_score", 0)),
                "confidence": float(parsed.get("confidence", 0)),
                "summary": str(parsed.get("summary", "")),
                "recommendation": str(parsed.get("recommendation", "")),
            }
        except (json.JSONDecodeError, ValueError, TypeError) as e:
            logger.error(f"Failed to parse LLM response: {e}")
            return {
                "problem_detected": False,
                "problem_type": "NONE",
                "problem_severity": "LOW",
                "risk_score": 0.0,
                "confidence": 0.0,
                "summary": "Analysis failed - defaulting to safe state.",
                "recommendation": "Continue monitoring - analysis error encountered.",
            }
