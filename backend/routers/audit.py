from __future__ import annotations

import json
import logging
from hashlib import sha256

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.auth import get_current_user
from backend.database import get_db
from backend.models import AuditLog
from backend.schemas import AuditEntryRequest, AuditEntryResponse

logger = logging.getLogger("smartbank.routers.audit")
router = APIRouter(prefix="/api/audit", tags=["Audit"])


@router.post("/log", response_model=AuditEntryResponse)
def audit_log(
    req: AuditEntryRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> AuditEntryResponse:
    last = db.query(AuditLog).order_by(AuditLog.id.desc()).first()
    prev_hash = last.hash if last else "0" * 64
    entry_str = json.dumps(
        {
            "action": req.action,
            "actor": req.actor or current_user.username,
            "resource": req.resource,
            "details": req.details,
            "previous_hash": prev_hash,
        },
        sort_keys=True,
    )
    h = sha256(entry_str.encode()).hexdigest()
    entry = AuditLog(
        action=req.action,
        actor=req.actor or current_user.username,
        resource=req.resource,
        details=req.details,
        previous_hash=prev_hash,
        hash=h,
    )
    db.add(entry)
    db.commit()
    return AuditEntryResponse(logged=True, entry_id=entry.id)


@router.get("/logs")
def audit_logs(
    limit: int = Query(50, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> dict:
    logs = (
        db.query(AuditLog)
        .order_by(AuditLog.id.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return {
        "logs": [
            {
                "id": l.id,
                "timestamp": l.timestamp.isoformat(),
                "action": l.action,
                "actor": l.actor,
                "resource": l.resource,
                "details": l.details,
                "hash": l.hash,
            }
            for l in logs
        ],
        "total": len(logs),
    }
