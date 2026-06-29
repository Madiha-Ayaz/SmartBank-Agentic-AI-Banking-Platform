from __future__ import annotations

import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from banking_api.database import get_db
from banking_api.models import Card, CardStatus
from banking_api.schemas import CardBlockRequest, CardBlockResponse, CardUnblockRequest, CardUnblockResponse

logger = logging.getLogger("banking_api.routers.cards")
router = APIRouter(prefix="/api/card", tags=["Card Management"])


@router.get("/list/{customer_id}", response_model=list[dict])
def list_cards(customer_id: str, db: Session = Depends(get_db)):
    cards = db.query(Card).filter(Card.customer_id == customer_id).all()
    return [c.to_dict() for c in cards]


@router.post("/block", response_model=CardBlockResponse)
def block_card(request: CardBlockRequest, db: Session = Depends(get_db)):
    if request.card_id:
        card = db.query(Card).filter(
            Card.card_id == request.card_id,
            Card.customer_id == request.customer_id,
        ).first()
    else:
        card = (
            db.query(Card)
            .filter(Card.customer_id == request.customer_id, Card.status == CardStatus.ACTIVE)
            .first()
        )

    if not card:
        raise HTTPException(status_code=404, detail="No active card found for customer")

    card.status = CardStatus.BLOCKED
    card.block_reason = request.reason
    db.commit()

    return CardBlockResponse(
        card_status="blocked",
        message=f"Card {card.card_id} blocked successfully. Reason: {request.reason}",
    )


@router.post("/unblock", response_model=CardUnblockResponse)
def unblock_card(request: CardUnblockRequest, db: Session = Depends(get_db)):
    card = db.query(Card).filter(
        Card.card_id == request.card_id,
        Card.customer_id == request.customer_id,
    ).first()

    if not card:
        raise HTTPException(status_code=404, detail="Card not found")

    if card.status != CardStatus.BLOCKED:
        raise HTTPException(status_code=400, detail="Card is not currently blocked")

    card.status = CardStatus.ACTIVE
    card.block_reason = ""
    db.commit()

    return CardUnblockResponse(
        card_status="active",
        message=f"Card {card.card_id} unblocked successfully",
    )
