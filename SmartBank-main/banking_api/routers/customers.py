from __future__ import annotations

import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from banking_api.database import get_db
from banking_api.models import Customer
from banking_api.schemas import CustomerResponse

logger = logging.getLogger("banking_api.routers.customers")
router = APIRouter(prefix="/api/customers", tags=["Customer Management"])


@router.get("/{customer_id}", response_model=CustomerResponse)
def get_customer(customer_id: str, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail=f"Customer {customer_id} not found")
    return customer.to_dict()


@router.get("", response_model=list[CustomerResponse])
def list_customers(db: Session = Depends(get_db)):
    customers = db.query(Customer).all()
    return [c.to_dict() for c in customers]
