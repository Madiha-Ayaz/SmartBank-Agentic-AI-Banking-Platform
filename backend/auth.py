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
from backend.models import User, AuthLog

logger = logging.getLogger("smartbank.auth")
security = HTTPBearer()

_jwks_cache: dict | None = None


def _get_firebase_public_keys() -> dict:
    global _jwks_cache
    if _jwks_cache is None:
        url = "https://www.googleapis.com/robot/v1/metadata/x509/securetoken@system.gserviceaccount.com"
        try:
            resp = urlopen(url)
            _jwks_cache = json.loads(resp.read())
        except Exception as exc:
            logger.error("Failed to fetch Firebase public keys: %s", exc)
            _jwks_cache = {}
    return _jwks_cache


def verify_firebase_token(token: str) -> Optional[dict[str, Any]]:
    keys = _get_firebase_public_keys()
    if not keys:
        raise HTTPException(status_code=500, detail="Auth misconfiguration")

    project_id = settings.FIREBASE_PROJECT_ID
    if not project_id:
        raise HTTPException(status_code=500, detail="FIREBASE_PROJECT_ID not set")

    for kid, pem in keys.items():
        try:
            payload = jwt.decode(
                token,
                pem,
                algorithms=["RS256"],
                audience=project_id,
                issuer=f"https://securetoken.google.com/{project_id}",
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
    payload = verify_firebase_token(credentials.credentials)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    uid: str = payload.get("uid", "")
    if not uid:
        raise HTTPException(status_code=401, detail="Invalid token: missing uid")

    email = payload.get("email", "") or ""
    username = email.split("@")[0] or uid[:8]

    user = db.query(User).filter(User.firebase_uid == uid).first()
    if user is None:
        user = User(firebase_uid=uid, username=username, email=email, role="agent")
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info("Auto-provisioned user firebase_uid=%s username=%s", uid, username)

    return user
