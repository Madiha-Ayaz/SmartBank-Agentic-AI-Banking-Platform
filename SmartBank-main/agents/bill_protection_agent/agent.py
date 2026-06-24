"""
SmartFinance AI — Smart Bill Protection Agent

Detects upcoming bills, predicts balance shortages, and prevents
failed payments through proactive customer notification and scheduling.

Technology: UiPath Agent Builder, LLM Agent, LangChain
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

logger = logging.getLogger("smartbank.agents.bill_protection")


@dataclass
class Bill:
    id: str
    biller_name: str
    category: str
    amount: float
    due_date: str
    status: str
    auto_pay: bool
    recurring: bool


@dataclass
class BillProtectionResult:
    customer_id: str
    at_risk_bills: list[dict]
    total_at_risk_amount: float
    current_balance: float
    projected_shortfall: float
    recommended_action: str
    requires_human_approval: bool
    analysis_summary: str
    confidence: float
    timestamp: str


class BillProtectionAgent:
    def __init__(self, config: Optional[dict[str, Any]] = None):
        self.config = config or {}
        self.min_balance_threshold = float(self.config.get("min_balance_threshold", 500.0))

    def analyze(
        self,
        customer_id: str,
        account_balance: float,
        upcoming_bills: list[Bill],
        recurring_expenses: list[dict],
        income_schedule: list[dict],
    ) -> BillProtectionResult:
        today = datetime.now(timezone.utc)
        at_risk: list[dict] = []
        total_at_risk = 0.0
        projected_outflow = 0.0

        for bill in sorted(upcoming_bills, key=lambda b: b.due_date):
            try:
                due = datetime.fromisoformat(bill.due_date)
                days_until_due = (due - today).days
            except (ValueError, TypeError):
                days_until_due = 7

            if days_until_due < 0:
                continue

            if days_until_due <= 3:
                projected_outflow += bill.amount
                balance_after = account_balance - projected_outflow

                if balance_after < self.min_balance_threshold:
                    at_risk.append({
                        "bill_id": bill.id,
                        "biller": bill.biller_name,
                        "amount": bill.amount,
                        "due_date": bill.due_date,
                        "days_until_due": days_until_due,
                        "balance_after": round(balance_after, 2),
                        "risk": "CRITICAL" if balance_after < 0 else "HIGH",
                    })
                    total_at_risk += bill.amount

            elif days_until_due <= 7:
                projected_outflow += bill.amount * 0.5

        shortfall = max(0, total_at_risk - account_balance)
        needs_approval = shortfall > 0 or total_at_risk > account_balance * 0.5

        if at_risk:
            bill_names = ", ".join(b["biller"] for b in at_risk)
            summary = f"{len(at_risk)} bill(s) at risk: {bill_names}. Shortfall: Rs.{shortfall:.0f}"
            if shortfall > 0:
                action = f"Insufficient balance. Recommend partial payment of Rs.{account_balance:.0f} or overdraft request."
            else:
                action = "Notify customer and suggest payment scheduling."
        else:
            summary = "No bills at immediate risk."
            action = "Continue monitoring - all upcoming bills are covered."

        return BillProtectionResult(
            customer_id=customer_id,
            at_risk_bills=at_risk,
            total_at_risk_amount=round(total_at_risk, 2),
            current_balance=round(account_balance, 2),
            projected_shortfall=round(shortfall, 2),
            recommended_action=action,
            requires_human_approval=needs_approval,
            analysis_summary=summary,
            confidence=0.92 if at_risk else 0.98,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
