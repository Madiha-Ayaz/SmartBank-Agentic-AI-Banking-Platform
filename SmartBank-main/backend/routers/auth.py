from __future__ import annotations

import logging

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.auth import get_current_user
from backend.database import get_db
from backend.models import User
from backend.schemas import UserResponse

logger = logging.getLogger("smartbank.routers.auth")
router = APIRouter(prefix="/api/auth", tags=["Authentication"])


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
