from __future__ import annotations

import logging

from fastapi import APIRouter, Request
from sqlalchemy.orm import Session

from backend.auth import get_current_user
from backend.database import get_db
from backend.models import Customer

logger = logging.getLogger("smartbank.routers.customers")
router = APIRouter(prefix="/api/customers", tags=["Customers"])


@router.get("")
def list_customers(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> dict:
    customers = db.query(Customer).all()
    return {
        "customers": [
            {"id": c.id, "name": c.name, "email": c.email, "phone": c.phone}
            for c in customers
        ]
    }


@router.post("")
async def create_customer(
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> dict:
    body = await request.json()
    c = Customer(
        name=body.get("name"),
        email=body.get("email"),
        phone=body.get("phone"),
    )
    db.add(c)
    db.commit()
    db.refresh(c)
    return {"id": c.id, "name": c.name, "email": c.email, "phone": c.phone}
