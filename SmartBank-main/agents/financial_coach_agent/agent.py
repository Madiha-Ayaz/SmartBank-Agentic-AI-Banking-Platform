"""
SmartFinance AI — Financial Health Coach Agent

Analyzes monthly spending, saving habits, and expenses to generate
personalized budget plans, saving recommendations, and spending alerts.

Technology: UiPath Agent Builder, LLM Agent, LangChain/CrewAI
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional

logger = logging.getLogger("smartbank.agents.financial_coach")


@dataclass
class SpendingCategory:
    name: str
    monthly_spend: float
    percentage: float
    trend: str
    is_subscription: bool


@dataclass
class CoachResult:
    customer_id: str
    health_score: float
    spending_analysis: list[dict]
    saving_opportunities: list[dict]
    budget_recommendations: list[str]
    total_monthly_savings_potential: float
    requires_human_review: bool
    analysis_summary: str
    confidence: float
    timestamp: str


class FinancialCoachAgent:
    def __init__(self, config: Optional[dict[str, Any]] = None):
        self.config = config or {}
        self.llm_api_key = self.config.get("llm_api_key", "")

    def analyze(
        self,
        customer_id: str,
        monthly_income: float,
        monthly_expenses: float,
        categories: list[SpendingCategory],
        savings_balance: float = 0.0,
        subscription_spend: float = 0.0,
    ) -> CoachResult:
        health_score = self._calculate_health_score(
            monthly_income, monthly_expenses, savings_balance
        )

        analysis = []
        for cat in categories:
            analysis.append({
                "category": cat.name,
                "monthly_spend": cat.monthly_spend,
                "percentage": cat.percentage,
                "trend": cat.trend,
                "is_subscription": cat.is_subscription,
                "benchmark": self._get_category_benchmark(cat.name, monthly_income),
                "status": "HIGH" if cat.percentage > 30 else "NORMAL" if cat.percentage < 20 else "MODERATE",
            })

        savings_opps = []
        total_savings = 0.0

        for entry in analysis:
            if entry["status"] == "HIGH" and entry["percentage"] > 25:
                potential_save = entry["monthly_spend"] * 0.15
                savings_opps.append({
                    "category": entry["category"],
                    "current_spend": entry["monthly_spend"],
                    "potential_saving": round(potential_save, 2),
                    "suggestion": f"Reduce {entry['category'].lower()} spending by 15% to save Rs.{potential_save:.0f}/month",
                })
                total_savings += potential_save

        if subscription_spend > 1000:
            savings_opps.append({
                "category": "Subscriptions",
                "current_spend": subscription_spend,
                "potential_saving": round(subscription_spend * 0.3, 2),
                "suggestion": f"Review recurring subscriptions. You could save Rs.{subscription_spend * 0.3:.0f}/month",
            })
            total_savings += subscription_spend * 0.3

        recommendations = []
        if health_score < 40:
            recommendations.append("Create an emergency fund covering 3 months of expenses")
            recommendations.append("Reduce discretionary spending by 20%")
        if monthly_expenses > monthly_income * 0.7:
            recommendations.append(f"Set a monthly budget cap of Rs.{monthly_income * 0.7:.0f}")
        if savings_balance < monthly_income * 3:
            recommendations.append("Increase monthly savings by 10% of income")
        if subscription_spend > 2000:
            recommendations.append("Audit and cancel unused subscriptions")

        if health_score < 30:
            summary = "Urgent: Financial health needs immediate attention. Spending exceeds healthy levels."
        elif health_score < 60:
            summary = f"Warning: Financial health is moderate. Potential savings of Rs.{total_savings:.0f}/month identified."
        else:
            summary = f"Good: Financial health is stable. You could save Rs.{total_savings:.0f} more monthly."

        return CoachResult(
            customer_id=customer_id,
            health_score=round(health_score, 1),
            spending_analysis=analysis,
            saving_opportunities=savings_opps,
            budget_recommendations=recommendations,
            total_monthly_savings_potential=round(total_savings, 2),
            requires_human_review=health_score < 25,
            analysis_summary=summary,
            confidence=0.88 if health_score < 60 else 0.93,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

    def _calculate_health_score(
        self, income: float, expenses: float, savings: float
    ) -> float:
        if income <= 0:
            return 10.0
        savings_rate = max(0, (income - expenses) / income) * 100
        expense_ratio = expenses / income

        score = 100.0
        if expense_ratio > 0.8:
            score -= 30
        elif expense_ratio > 0.6:
            score -= 15
        if savings_rate < 5:
            score -= 20
        elif savings_rate < 15:
            score -= 10
        if savings < 10000:
            score -= 15
        elif savings < 50000:
            score -= 5

        return max(0, min(100, score))

    def _get_category_benchmark(self, category: str, income: float) -> str:
        benchmarks = {
            "Housing": "25-30%",
            "Food": "10-15%",
            "Transport": "10-15%",
            "Utilities": "5-10%",
            "Entertainment": "5-10%",
            "Shopping": "5-10%",
            "Healthcare": "5-10%",
            "Education": "5-15%",
            "Subscriptions": "2-5%",
        }
        return benchmarks.get(category, "5-15%")
