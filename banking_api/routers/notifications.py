from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from banking_api.database import get_db
from banking_api.models import Notification, Customer
from banking_api.schemas import NotificationRequest, NotificationResponse

logger = logging.getLogger("banking_api.routers.notifications")
router = APIRouter(prefix="/api/notification", tags=["Notification API"])

VALID_CHANNELS = {"SMS", "EMAIL", "WHATSAPP", "PUSH"}


@router.post("/send", response_model=NotificationResponse)
def send_notification(request: NotificationRequest, db: Session = Depends(get_db)):
    if request.channel.upper() not in VALID_CHANNELS:
        raise HTTPException(status_code=400, detail=f"Invalid channel: {request.channel}. Must be one of {VALID_CHANNELS}")

    customer = db.query(Customer).filter(Customer.customer_id == request.customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail=f"Customer {request.customer_id} not found")

    notif_id = f"NOT{uuid.uuid4().hex[:8].upper()}"
    notification = Notification(
        notification_id=notif_id,
        customer_id=request.customer_id,
        channel=request.channel.upper(),
        message=request.message,
        status="sent",
        created_at=datetime.now(timezone.utc),
    )
    db.add(notification)
    db.commit()

    logger.info(f"Notification {notif_id} sent to {request.customer_id} via {request.channel}")

    return NotificationResponse(
        notification_id=notif_id,
        status="sent",
        channel=request.channel.upper(),
    )


@router.get("/history/{customer_id}", response_model=list[dict])
def notification_history(customer_id: str, db: Session = Depends(get_db)):
    notifications = (
        db.query(Notification)
        .filter(Notification.customer_id == customer_id)
        .order_by(Notification.created_at.desc())
        .limit(50)
        .all()
    )
    return [n.to_dict() for n in notifications]
