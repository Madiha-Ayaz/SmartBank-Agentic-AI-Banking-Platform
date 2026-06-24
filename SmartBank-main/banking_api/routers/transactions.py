from __future__ import annotations

import logging
import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from banking_api.database import get_db
from banking_api.models import Transaction, Account, TransactionType, TransactionStatus
from banking_api.schemas import TransactionResponse

logger = logging.getLogger("banking_api.routers.transactions")
router = APIRouter(prefix="/api/transactions", tags=["Transaction History"])


@router.get("/{customer_id}", response_model=list[TransactionResponse])
def get_transaction_history(
    customer_id: str,
    limit: int = Query(50, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    transactions = (
        db.query(Transaction)
        .filter(Transaction.customer_id == customer_id)
        .order_by(desc(Transaction.created_at))
        .offset(offset)
        .limit(limit)
        .all()
    )
    if not transactions:
        return []
    return [t.to_dict() for t in transactions]


@router.get("/detail/{transaction_id}", response_model=TransactionResponse)
def get_transaction_detail(transaction_id: str, db: Session = Depends(get_db)):
    txn = db.query(Transaction).filter(Transaction.transaction_id == transaction_id).first()
    if not txn:
        raise HTTPException(status_code=404, detail=f"Transaction {transaction_id} not found")
    return txn.to_dict()
