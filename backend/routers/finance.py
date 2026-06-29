from __future__ import annotations

import logging
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional

from backend.database import SessionLocal
from backend.models import FinanceCustomer, FinanceTransaction, gen_id

logger = logging.getLogger("smartbank.routers.finance")
router = APIRouter(prefix="/api/finance", tags=["Finance"])


class TransferRequest(BaseModel):
    sender_account: str
    receiver_account: str
    amount: float = Field(gt=0)
    description: Optional[str] = None
    password: Optional[str] = None


class TransferResponse(BaseModel):
    success: bool
    transaction_id: Optional[str] = None
    sender_name: Optional[str] = None
    receiver_name: Optional[str] = None
    amount: Optional[float] = None
    sender_new_balance: Optional[float] = None
    receiver_new_balance: Optional[float] = None
    message: str


class CustomerResponse(BaseModel):
    customer_id: int
    full_name: str
    account_number: str
    account_balance: float
    credit_score: int
    phone: Optional[str] = None
    email: Optional[str] = None
    city: Optional[str] = None
    profession: Optional[str] = None


class TransactionHistoryItem(BaseModel):
    id: str
    sender_account: str
    receiver_account: str
    sender_name: Optional[str] = None
    receiver_name: Optional[str] = None
    amount: float
    type: str
    status: str
    description: Optional[str] = None
    created_at: str


@router.post("/transfer", response_model=TransferResponse)
def transfer_money(body: TransferRequest):
    if body.sender_account == body.receiver_account:
        raise HTTPException(status_code=400, detail="Sender and receiver must be different")

    db = SessionLocal()
    try:
        sender = db.query(FinanceCustomer).filter(
            FinanceCustomer.account_number == body.sender_account
        ).first()
        if not sender:
            raise HTTPException(status_code=404, detail="Sender account not found")

        if body.password and sender.password and body.password != sender.password:
            raise HTTPException(status_code=401, detail="Invalid password")

        receiver = db.query(FinanceCustomer).filter(
            FinanceCustomer.account_number == body.receiver_account
        ).first()
        if not receiver:
            raise HTTPException(status_code=404, detail="Receiver account not found")

        if sender.account_balance < body.amount:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient balance. Available: {sender.account_balance:,.2f}",
            )

        sender.account_balance -= body.amount
        receiver.account_balance += body.amount

        txn = FinanceTransaction(
            id=gen_id(),
            sender_account=body.sender_account,
            receiver_account=body.receiver_account,
            sender_name=sender.full_name,
            receiver_name=receiver.full_name,
            amount=body.amount,
            type="transfer",
            status="completed",
            description=body.description or f"Transfer from {sender.full_name} to {receiver.full_name}",
        )
        db.add(txn)
        db.commit()
        db.refresh(txn)

        logger.info(
            f"Transfer: {sender.full_name} -> {receiver.full_name}, "
            f"Amount: {body.amount:,.2f}, TXN: {txn.id}"
        )

        return TransferResponse(
            success=True,
            transaction_id=txn.id,
            sender_name=sender.full_name,
            receiver_name=receiver.full_name,
            amount=body.amount,
            sender_new_balance=sender.account_balance,
            receiver_new_balance=receiver.account_balance,
            message=f"Transfer successful! ${body.amount:,.2f} sent from {sender.full_name} to {receiver.full_name}.",
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Transfer failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@router.get("/customer/{account_number}", response_model=CustomerResponse)
def get_customer(account_number: str):
    db = SessionLocal()
    try:
        customer = db.query(FinanceCustomer).filter(
            FinanceCustomer.account_number == account_number
        ).first()
        if not customer:
            raise HTTPException(status_code=404, detail="Account not found")
        return CustomerResponse(
            customer_id=customer.customer_id,
            full_name=customer.full_name,
            account_number=customer.account_number,
            account_balance=customer.account_balance,
            credit_score=customer.credit_score,
            phone=customer.phone,
            email=customer.email,
            city=customer.city,
            profession=customer.profession,
        )
    finally:
        db.close()


@router.get("/customer/search", response_model=list[CustomerResponse])
def search_customers(q: str = Query("", description="Search by name, account, or phone")):
    db = SessionLocal()
    try:
        query = db.query(FinanceCustomer)
        if q:
            like = f"%{q}%"
            query = query.filter(
                FinanceCustomer.full_name.ilike(like)
                | FinanceCustomer.account_number.ilike(like)
                | FinanceCustomer.phone.ilike(like)
            )
        customers = query.limit(20).all()
        return [
            CustomerResponse(
                customer_id=c.customer_id,
                full_name=c.full_name,
                account_number=c.account_number,
                account_balance=c.account_balance,
                credit_score=c.credit_score,
                phone=c.phone,
                email=c.email,
                city=c.city,
                profession=c.profession,
            )
            for c in customers
        ]
    finally:
        db.close()


@router.get("/transactions/{account_number}", response_model=list[TransactionHistoryItem])
def get_transactions(account_number: str, limit: int = Query(20, ge=1, le=100)):
    db = SessionLocal()
    try:
        customer = db.query(FinanceCustomer).filter(
            FinanceCustomer.account_number == account_number
        ).first()
        if not customer:
            raise HTTPException(status_code=404, detail="Account not found")

        txns = (
            db.query(FinanceTransaction)
            .filter(
                (FinanceTransaction.sender_account == account_number)
                | (FinanceTransaction.receiver_account == account_number)
            )
            .order_by(FinanceTransaction.created_at.desc())
            .limit(limit)
            .all()
        )
        return [
            TransactionHistoryItem(
                id=t.id,
                sender_account=t.sender_account,
                receiver_account=t.receiver_account,
                sender_name=t.sender_name,
                receiver_name=t.receiver_name,
                amount=t.amount,
                type=t.type,
                status=t.status,
                description=t.description,
                created_at=t.created_at.isoformat() if t.created_at else "",
            )
            for t in txns
        ]
    finally:
        db.close()


@router.get("/count")
def get_customer_count():
    db = SessionLocal()
    try:
        count = db.query(FinanceCustomer).count()
        return {"total_customers": count}
    finally:
        db.close()
