from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from banking_api.database import get_db
from banking_api.models import Account, Transaction, AccountStatus, TransactionStatus, TransactionType
from banking_api.schemas import PaymentRequest, PaymentResponse

logger = logging.getLogger("banking_api.routers.payments")
router = APIRouter(prefix="/api/payment", tags=["Payment Processing"])


@router.post("/process", response_model=PaymentResponse)
def process_payment(request: PaymentRequest, db: Session = Depends(get_db)):
    account = db.query(Account).filter(Account.account_id == request.account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail=f"Account {request.account_id} not found")

    if account.account_status != AccountStatus.ACTIVE:
        raise HTTPException(status_code=400, detail=f"Account is {account.account_status.value}")

    if account.balance < request.amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")

    txn_id = f"TX{uuid.uuid4().hex[:8].upper()}"

    account.balance -= request.amount

    txn = Transaction(
        transaction_id=txn_id,
        customer_id=account.customer_id,
        account_id=request.account_id,
        amount=request.amount,
        currency=account.currency,
        merchant=request.merchant,
        category=request.category,
        transaction_type=TransactionType.PAYMENT,
        status=TransactionStatus.COMPLETED,
        location="Online",
        is_online=True,
        created_at=datetime.now(timezone.utc),
    )
    db.add(txn)
    db.commit()

    return PaymentResponse(
        transaction_id=txn_id,
        payment_status="success",
        message=f"Payment of Rs.{request.amount:.0f} to {request.merchant} completed",
        balance_after=round(account.balance, 2),
    )
