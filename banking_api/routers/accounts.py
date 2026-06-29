from __future__ import annotations

import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from banking_api.database import get_db
from banking_api.models import Account
from banking_api.schemas import AccountBalanceResponse

logger = logging.getLogger("banking_api.routers.accounts")
router = APIRouter(prefix="/api/accounts", tags=["Account Balance"])


@router.get("/{account_id}/balance", response_model=AccountBalanceResponse)
def get_account_balance(account_id: str, db: Session = Depends(get_db)):
    account = db.query(Account).filter(Account.account_id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail=f"Account {account_id} not found")
    return account.to_dict()


@router.get("/customer/{customer_id}", response_model=list[AccountBalanceResponse])
def get_customer_accounts(customer_id: str, db: Session = Depends(get_db)):
    accounts = db.query(Account).filter(Account.customer_id == customer_id).all()
    if not accounts:
        raise HTTPException(status_code=404, detail=f"No accounts found for customer {customer_id}")
    return [a.to_dict() for a in accounts]
