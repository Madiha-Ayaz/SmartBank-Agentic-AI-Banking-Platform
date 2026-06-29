from __future__ import annotations

import json
import logging
import random
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from banking_api.database import get_db
from banking_api.models import FraudCase, Transaction, Customer, FraudStatus, RiskLevel
from banking_api.schemas import FraudCheckRequest, FraudCheckResponse

logger = logging.getLogger("banking_api.routers.fraud")
router = APIRouter(prefix="/api/fraud", tags=["Fraud Detection"])

FRAUD_INDICATORS = {
    "high_amount": lambda a, h: a > 50000,
    "international_location": lambda t, h: t.get("is_international", False),
    "unusual_merchant": lambda t, h: t.get("merchant", "") not in [x.get("merchant") for x in h[-10:]],
    "rapid_transaction": lambda t, h: len([x for x in h[-5:] if x.get("status") == "completed"]) > 3,
    "amount_anomaly": lambda a, h: len(h) > 0 and a > sum(x.get("amount", 0) for x in h[-10:]) / max(len(h[-10:]), 1) * 3,
    "off_hours": lambda t, h: _is_off_hours(),
    "new_location": lambda t, h: t.get("location", "") not in [x.get("location") for x in h[-20:]],
}


def _is_off_hours():
    hour = datetime.now(timezone.utc).hour
    return hour < 6 or hour > 23


def _calculate_risk_score(amount: float, transaction: dict, history: list[dict]) -> tuple[float, str, list[str]]:
    score = 0.0
    triggered = []

    if FRAUD_INDICATORS["high_amount"](amount, history):
        score += 30
        triggered.append("High transaction amount exceeds threshold")

    if FRAUD_INDICATORS["international_location"](transaction, history):
        score += 25
        triggered.append("International transaction detected")

    if FRAUD_INDICATORS["unusual_merchant"](transaction, history):
        score += 15
        triggered.append("Transaction with unknown merchant")

    if FRAUD_INDICATORS["amount_anomaly"](amount, history):
        score += 20
        triggered.append("Amount significantly deviates from spending pattern")

    if FRAUD_INDICATORS["off_hours"](transaction, history):
        score += 10
        triggered.append("Transaction occurred during off-hours")

    if FRAUD_INDICATORS["new_location"](transaction, history):
        score += 15
        triggered.append("Transaction from new/unusual location")

    score = min(100, score)

    if score >= 70:
        level = "CRITICAL"
        action = "immediate_block_and_notify"
    elif score >= 50:
        level = "HIGH"
        action = "human_review"
    elif score >= 25:
        level = "MEDIUM"
        action = "flag_for_review"
    else:
        level = "LOW"
        action = "auto_approve"

    return round(score, 1), level, triggered


@router.post("/check", response_model=FraudCheckResponse)
def check_fraud(request: FraudCheckRequest, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.customer_id == request.customer_id).first()

    history = (
        db.query(Transaction)
        .filter(Transaction.customer_id == request.customer_id)
        .order_by(Transaction.created_at.desc())
        .limit(50)
        .all()
    )
    history_dicts = [t.to_dict() for t in history]

    transaction_data = {
        "customer_id": request.customer_id,
        "transaction_id": request.transaction_id,
        "merchant": request.merchant,
        "location": request.location,
        "is_international": request.is_international,
    }

    risk_score, risk_level, indicators = _calculate_risk_score(
        request.amount, transaction_data, history_dicts
    )

    if risk_level == "LOW":
        action = "auto_approve"
    elif risk_level == "MEDIUM":
        action = "flag_for_review"
    elif risk_level == "HIGH":
        action = "human_review"
    else:
        action = "immediate_block_and_notify"

    case_id = f"FR-{uuid.uuid4().hex[:8].upper()}"
    fraud_case = FraudCase(
        case_id=case_id,
        transaction_id=request.transaction_id,
        customer_id=request.customer_id,
        risk_score=risk_score,
        risk_level=risk_level,
        indicators=json.dumps(indicators),
        status=FraudStatus.OPEN,
        recommended_action=action,
    )
    db.add(fraud_case)

    if risk_level in ("HIGH", "CRITICAL") and customer:
        customer.risk_level = RiskLevel.HIGH

    db.commit()

    return FraudCheckResponse(
        risk_score=risk_score,
        risk_level=risk_level,
        recommended_action=action,
        indicators=indicators,
        case_id=case_id,
    )


@router.get("/cases/{customer_id}", response_model=list[dict])
def list_fraud_cases(customer_id: str, db: Session = Depends(get_db)):
    cases = (
        db.query(FraudCase)
        .filter(FraudCase.customer_id == customer_id)
        .order_by(FraudCase.created_at.desc())
        .all()
    )
    return [c.to_dict() for c in cases]


@router.post("/cases/{case_id}/resolve")
def resolve_fraud_case(case_id: str, db: Session = Depends(get_db)):
    case = db.query(FraudCase).filter(FraudCase.case_id == case_id).first()
    if not case:
        return {"error": "Case not found"}
    case.status = FraudStatus.RESOLVED
    case.resolved_at = datetime.now(timezone.utc)
    db.commit()
    return {"status": "resolved", "case_id": case_id}
