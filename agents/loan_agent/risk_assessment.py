import math
import logging
from typing import Any

logger = logging.getLogger("smartbank.loan_agent.risk")


def calculate_risk(application: dict) -> dict:
    data = application.get("data_collected", {})
    emp_type = data.get("employment_type", "")

    income = _get_income(data, emp_type)
    expenses = _get_expenses(data, emp_type)
    loan_amount = data.get("loan_amount", 0) or 0
    duration = data.get("repayment_duration_months", 12) or 12

    debt_ratio = _calc_debt_ratio(income, expenses)
    income_stability = _calc_income_stability(data, emp_type)
    repayment_capability = _calc_repayment_capability(income, expenses, loan_amount, duration)
    credit_score = _calc_credit_score(debt_ratio, income_stability, repayment_capability, duration)
    risk_level, risk_factors = _determine_risk(
        debt_ratio, income_stability, repayment_capability, credit_score, loan_amount, income
    )

    return {
        "income_stability_score": round(income_stability, 2),
        "debt_ratio": round(debt_ratio, 2),
        "repayment_capability_score": round(repayment_capability, 2),
        "credit_score": credit_score,
        "risk_level": risk_level,
        "risk_factors": risk_factors,
    }


def _get_income(data: dict, emp_type: str) -> float:
    if emp_type in ("business_owner", "self_employed"):
        return data.get("monthly_profit", 0) or 0
    return data.get("monthly_salary", 0) or 0


def _get_expenses(data: dict, emp_type: str) -> float:
    if emp_type in ("business_owner", "self_employed"):
        return data.get("business_expenses", 0) or 0
    return data.get("monthly_expenses", 0) or 0


def _calc_debt_ratio(income: float, expenses: float) -> float:
    if income <= 0:
        return 1.0
    return min(expenses / income, 2.0)


def _calc_income_stability(data: dict, emp_type: str) -> float:
    if emp_type == "employee":
        years = data.get("employment_duration_years", 0) or 0
        if years >= 5:
            return 0.9
        elif years >= 3:
            return 0.75
        elif years >= 1:
            return 0.6
        else:
            return 0.4
    else:
        years = data.get("business_years", 0) or 0
        if years >= 5:
            return 0.85
        elif years >= 3:
            return 0.7
        elif years >= 1:
            return 0.55
        else:
            return 0.35


def _calc_repayment_capability(income: float, expenses: float, loan_amount: float, duration: int) -> float:
    if income <= 0 or duration <= 0:
        return 0.0
    disposable = income - expenses
    if disposable <= 0:
        return 0.1
    monthly_payment = loan_amount / duration
    ratio = monthly_payment / disposable
    if ratio <= 0.2:
        return 0.9
    elif ratio <= 0.35:
        return 0.7
    elif ratio <= 0.5:
        return 0.5
    else:
        return 0.3


def _calc_credit_score(
    debt_ratio: float,
    income_stability: float,
    repayment_capability: float,
    duration: int,
) -> int:
    base = 300
    debt_score = (1 - debt_ratio) * 200
    stability_score = income_stability * 200
    repayment_score = repayment_capability * 200
    duration_penalty = max(0, (duration - 60)) * 0.5
    score = base + debt_score + stability_score + repayment_score - duration_penalty
    return min(max(int(score), 300), 850)


def _determine_risk(
    debt_ratio: float,
    income_stability: float,
    repayment_capability: float,
    credit_score: int,
    loan_amount: float,
    income: float,
) -> tuple[str, list[str]]:
    factors = []

    if debt_ratio > 0.6:
        factors.append("High debt-to-income ratio")
    if income_stability < 0.5:
        factors.append("Short employment/business history")
    if repayment_capability < 0.4:
        factors.append("Monthly payment too high relative to disposable income")
    if credit_score < 500:
        factors.append("Below average credit score")
    if loan_amount > income * 12 * 3:
        factors.append("Loan amount significantly exceeds annual income multiple")

    if credit_score >= 700 and debt_ratio <= 0.4 and repayment_capability >= 0.7:
        return "low", factors
    elif credit_score >= 500 and debt_ratio <= 0.6 and repayment_capability >= 0.4:
        return "medium", factors
    else:
        return "high", factors


def decide_loan(risk_result: dict, application: dict) -> dict:
    risk_level = risk_result.get("risk_level", "high")
    data = application.get("data_collected", {})
    loan_amount = data.get("loan_amount", 0) or 0
    duration = data.get("repayment_duration_months", 12) or 12

    if risk_level == "low":
        interest_rate = 12.0
        approved = True
        reason = "Your application meets our lending criteria with strong income stability and credit profile."
    elif risk_level == "medium":
        interest_rate = 16.0
        approved = True
        reason = "Your application has been approved with standard terms based on your credit profile."
    else:
        approved = False
        interest_rate = 0
        reason = "Your application does not meet our current lending criteria due to high risk factors."

    monthly_rate = (interest_rate / 100) / 12
    if monthly_rate > 0 and approved:
        monthly_payment = loan_amount * (monthly_rate * (1 + monthly_rate) ** duration) / ((1 + monthly_rate) ** duration - 1)
    else:
        monthly_payment = loan_amount / duration if duration > 0 else 0

    total_payment = monthly_payment * duration
    late_fee = 2.0

    suggestions = []
    if not approved:
        if risk_level == "high":
            if "High debt-to-income ratio" in (risk_result.get("risk_factors") or []):
                suggestions.append("Reduce your monthly expenses or increase income before reapplying")
            if "Short employment/business history" in (risk_result.get("risk_factors") or []):
                suggestions.append("Build a longer employment/business track record")
            if "Loan amount significantly exceeds annual income multiple" in (risk_result.get("risk_factors") or []):
                suggestions.append("Consider applying for a lower loan amount")
        suggestions.append("Improve your credit score by making timely payments on existing obligations")
        suggestions.append("Consider applying with a co-signer or guarantor")

    return {
        "approved": approved,
        "decision_reason": reason,
        "improvement_suggestions": suggestions if suggestions else None,
        "interest_rate": interest_rate,
        "monthly_payment": round(monthly_payment, 2),
        "total_payment": round(total_payment, 2),
        "late_payment_charge_rate": late_fee,
    }
