from __future__ import annotations

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.auth import get_current_user
from backend.cache import cache
from backend.database import get_db
from backend.models import Case
from backend.schemas import (
    AnalyticsResponse,
    CaseListResponse,
    CaseResponse,
    StatsResponse,
)

logger = logging.getLogger("smartbank.routers.dashboard")
router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/stats", response_model=StatsResponse)
async def dashboard_stats(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> StatsResponse:
    cached = await cache.get("dashboard:stats")
    if cached:
        return StatsResponse(**cached)

    cases = db.query(Case).all()
    total = len(cases)
    resolved = sum(1 for c in cases if c.status == "Resolved")
    pending = sum(1 for c in cases if c.status in ("Pending", "In Progress", "OTP Sent"))
    human_review = sum(1 for c in cases if c.status == "Human Review")
    critical = sum(1 for c in cases if c.priority == "Critical")

    times = [c.time for c in cases if c.time != "\u2014"]
    avg_time = "0s"
    if times:
        secs = []
        for t in times:
            if "s" in t:
                secs.append(int(t.replace("s", "")))
            elif "m" in t:
                secs.append(int(t.replace("m", "")) * 60)
        if secs:
            a = sum(secs) / len(secs)
            avg_time = f"{a:.0f}s" if a < 60 else f"{a / 60:.0f}m"

    auto_rate = round((resolved / total) * 100) if total else 0
    result = StatsResponse(
        total_cases=total,
        resolved=resolved,
        pending=pending,
        human_review=human_review,
        critical=critical,
        avg_resolution_time=avg_time,
        automation_rate=auto_rate,
        sla_compliance=92,
    )
    await cache.set("dashboard:stats", result.model_dump(), ttl=60)
    return result


@router.get("/cases", response_model=CaseListResponse)
def list_cases(
    search: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> CaseListResponse:
    q = db.query(Case)
    if search:
        s = search.lower()
        q = q.filter(
            Case.id.ilike(f"%{s}%")
            | Case.customer_name.ilike(f"%{s}%")
            | Case.type.ilike(f"%{s}%")
        )
    if status:
        q = q.filter(Case.status.ilike(status))
    if priority:
        q = q.filter(Case.priority.ilike(priority))

    total = q.count()
    results = q.offset((page - 1) * page_size).limit(page_size).all()

    return CaseListResponse(
        cases=[
            CaseResponse(
                id=c.id,
                customer_name=c.customer_name,
                type=c.type,
                status=c.status,
                priority=c.priority,
                channel=c.channel,
                time=c.time,
                date=c.date,
            )
            for c in results
        ],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/cases/{case_id}", response_model=CaseResponse)
def get_case(
    case_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> CaseResponse:
    c = db.query(Case).filter(Case.id == case_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Case not found")
    return CaseResponse(
        id=c.id,
        customer_name=c.customer_name,
        type=c.type,
        status=c.status,
        priority=c.priority,
        channel=c.channel,
        time=c.time,
        date=c.date,
    )


@router.get("/analytics", response_model=AnalyticsResponse)
def analytics(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> AnalyticsResponse:
    cases = db.query(Case).all()
    by_status: dict[str, int] = {}
    by_priority: dict[str, int] = {}
    by_channel: dict[str, int] = {}
    for c in cases:
        by_status[c.status] = by_status.get(c.status, 0) + 1
        by_priority[c.priority] = by_priority.get(c.priority, 0) + 1
        by_channel[c.channel] = by_channel.get(c.channel, 0) + 1
    return AnalyticsResponse(
        by_status=by_status,
        by_priority=by_priority,
        by_channel=by_channel,
    )
