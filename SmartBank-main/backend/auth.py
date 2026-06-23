from __future__ import annotations

import json
import logging
from typing import Any, Optional
from urllib.request import urlopen

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from backend.config import settings
from backend.database import get_db
from backend.models import User

logger = logging.getLogger("smartbank.auth")
security = HTTPBearer()

_jwks_cache: list[dict] | None = None


def _get_jwks() -> list[dict]:
    global _jwks_cache
    if _jwks_cache is None:
        try:
            resp = urlopen(settings.CLERK_JWKS_URL)
            _jwks_cache = json.loads(resp.read()).get("keys", [])
        except Exception as exc:
            logger.error("Failed to fetch Clerk JWKS: %s", exc)
            _jwks_cache = []
    return _jwks_cache


def verify_clerk_token(token: str) -> Optional[dict[str, Any]]:
    jwks = _get_jwks()
    if not jwks:
        raise HTTPException(status_code=500, detail="Auth misconfiguration")

    for key in jwks:
        try:
            payload = jwt.decode(
                token,
                key,
                algorithms=["RS256"],
                audience=settings.CLERK_PUBLISHABLE_KEY,
                issuer=settings.CLERK_ISSUER,
                options={"verify_exp": True},
            )
            return payload
        except jwt.PyJWTError:
            continue
    return None


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    payload = verify_clerk_token(credentials.credentials)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    clerk_id: str = payload.get("sub", "")
    if not clerk_id:
        raise HTTPException(status_code=401, detail="Invalid token: missing sub")

    user = db.query(User).filter(User.clerk_id == clerk_id).first()
    if user is None:
        # Auto-provision user from Clerk session on first access
        email = (payload.get("email") or payload.get("preferred_username") or "")
        username = email.split("@")[0] or clerk_id[:8]
        user = User(clerk_id=clerk_id, username=username, email=email, role="agent")
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info("Auto-provisioned user clerk_id=%s username=%s", clerk_id, username)

    return user
