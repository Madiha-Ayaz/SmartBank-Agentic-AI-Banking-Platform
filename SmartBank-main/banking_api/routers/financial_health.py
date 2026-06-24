from __future__ import annotations

import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from banking_api.database import get_db
from banking_api.models import Customer, Transaction
from banking_api.schemas import FinancialHealthResponse

logger = logging.getLogger("banking_api.routers.financial_health")
router = APIRouter(prefix="/api/financial-health", tags=["Financial Health"])


@router.get("/{customer_id}", response_model=FinancialHealthResponse)
def get_financial_health(customer_id: str, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail=f"Customer {customer_id} not found")

    transactions = (
        db.query(Transaction)
        .filter(Transaction.customer_id == customer_id)
        .order_by(Transaction.created_at.desc())
        .limit(100)
        .all()
    )

    income = customer.monthly_income or 80000
    expense = customer.monthly_expense or 0

    spending_by_category: dict[str, float] = {}
    for txn in transactions:
        if txn.transaction_type in ("debit", "payment") and txn.status == "completed":
            cat = txn.category or "General"
            spending_by_category[cat] = spending_by_category.get(cat, 0) + txn.amount

    if expense == 0:
        expense = sum(spending_by_category.values())

    savings_rate = max(0, (income - expense) / income * 100) if income > 0 else 0
    saving_score = min(100, savings_rate * 2 + 20)

    if spending_by_category:
        total = sum(spending_by_category.values())
        spending_breakdown = [
            {"category": cat, "amount": round(amt, 2), "percentage": round(amt / total * 100, 1)}
            for cat, amt in sorted(spending_by_category.items(), key=lambda x: -x[1])
        ]
    else:
        spending_breakdown = []

    top_category = spending_breakdown[0]["category"] if spending_breakdown else "General"

    recommendations = []
    saving_potential = 0

    if savings_rate < 10:
        recommendations.append("Increase monthly savings to at least 10% of income")
        saving_potential += income * 0.05
    if top_category in ("Shopping", "Entertainment") and spending_by_category.get(top_category, 0) > income * 0.3:
        recommendations.append(f"Reduce {top_category.lower()} expenses by 20%")
        saving_potential += spending_by_category.get(top_category, 0) * 0.2
    if any("subscription" in cat.lower() for cat in spending_by_category):
        recommendations.append("Review recurring subscriptions and cancel unused services")
        saving_potential += 2500
    if not recommendations:
        recommendations.append("Maintain your current spending habits. Consider investing surplus income.")

    return FinancialHealthResponse(
        customer_id=customer_id,
        monthly_income=income,
        monthly_expense=round(expense, 2),
        saving_score=round(saving_score, 1),
        saving_potential=round(saving_potential, 2),
        recommendation=recommendations[0] if recommendations else "Financial health is stable",
        spending_breakdown=spending_breakdown,
    )
