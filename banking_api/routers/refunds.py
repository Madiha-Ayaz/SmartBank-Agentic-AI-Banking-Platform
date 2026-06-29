from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from banking_api.database import get_db
from banking_api.models import Transaction, Account, TransactionStatus, TransactionType
from banking_api.schemas import RefundRequest, RefundResponse

logger = logging.getLogger("banking_api.routers.refunds")
router = APIRouter(prefix="/api/refund", tags=["Refund Management"])


@router.post("/create", response_model=RefundResponse)
def create_refund(request: RefundRequest, db: Session = Depends(get_db)):
    original_txn = db.query(Transaction).filter(
        Transaction.transaction_id == request.transaction_id
    ).first()

    if not original_txn:
        raise HTTPException(status_code=404, detail=f"Transaction {request.transaction_id} not found")

    if original_txn.status == TransactionStatus.REFUNDED:
        raise HTTPException(status_code=400, detail="Transaction already refunded")

    refund_id = f"RF{uuid.uuid4().hex[:8].upper()}"

    original_txn.status = TransactionStatus.REFUNDED

    account = db.query(Account).filter(Account.account_id == original_txn.account_id).first()
    if account:
        account.balance += original_txn.amount

    refund_txn = Transaction(
        transaction_id=f"RX{uuid.uuid4().hex[:8].upper()}",
        customer_id=original_txn.customer_id,
        account_id=original_txn.account_id,
        amount=original_txn.amount,
        currency=original_txn.currency,
        merchant=original_txn.merchant,
        merchant_ref=original_txn.merchant_ref,
        category=original_txn.category,
        transaction_type=TransactionType.REFUND,
        status=TransactionStatus.COMPLETED,
        location=original_txn.location,
        failure_reason=request.reason,
        created_at=datetime.now(timezone.utc),
    )
    db.add(refund_txn)
    db.commit()

    return RefundResponse(
        refund_id=refund_id,
        status="initiated",
        estimated_days=5,
        message=f"Refund of Rs.{original_txn.amount:.0f} initiated for transaction {request.transaction_id}",
    )
