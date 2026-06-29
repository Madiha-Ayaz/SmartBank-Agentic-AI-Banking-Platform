from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from backend.auth import get_current_user
from backend.database import get_db
from backend.models import User, AuthLog
from backend.schemas import UserResponse

logger = logging.getLogger("smartbank.routers.auth")
router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/activity")
def log_auth_activity(payload: dict, request: Request, db: Session = Depends(get_db)):
    log = AuthLog(
        action=payload.get("action", "unknown"),
        email=payload.get("email"),
        uid=payload.get("uid"),
        name=payload.get("name"),
        ip_address=request.client.host if request.client else None,
    )
    db.add(log)
    db.commit()
    return {"logged": True}


@router.get("/me", response_model=UserResponse)
def auth_me(current_user=Depends(get_current_user)) -> UserResponse:
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email or "",
        role=current_user.role,
    )


@router.post("/sync", response_model=UserResponse)
def sync_user(
    payload: dict,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> UserResponse:
    if "email" in payload and payload["email"]:
        current_user.email = payload["email"]
        db.commit()
        db.refresh(current_user)
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email or "",
        role=current_user.role,
    )
