from __future__ import annotations

import os
from pathlib import Path

import uvicorn
import logging

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

logger = logging.getLogger("smartbank.main")

from backend.config import settings
from backend.database import init_db, SessionLocal
from backend.log_setup import setup_logging
from backend.middleware import register_middleware
from backend.models import Case, User
from backend.auth import _get_jwks

setup_logging()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Agentic AI Banking Operations Platform",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_middleware(app)

from backend.routers import auth, dashboard, classify, chat, document, audit, workflows, robots, customers, smartfinance

app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(classify.router)
app.include_router(chat.router)
app.include_router(document.router)
app.include_router(audit.router)
app.include_router(workflows.router)
app.include_router(robots.router)
app.include_router(customers.router)
app.include_router(smartfinance.router)

from backend.websocket_manager import ws_manager


@app.websocket("/ws/dashboard")
async def websocket_dashboard(ws: WebSocket):
    await ws_manager.connect(ws, room="dashboard")
    try:
        while True:
            data = await ws.receive_text()
            if data == "ping":
                await ws.send_text('{"event":"pong"}')
    except WebSocketDisconnect:
        ws_manager.disconnect(ws, room="dashboard")
    except Exception:
        ws_manager.disconnect(ws, room="dashboard")

SAMPLE_CASES = [
    {"id": "REQ-001", "customer": "Ali Ahmed", "type": "Card Block", "status": "Resolved", "priority": "Critical", "time": "42s", "date": "2026-06-20", "channel": "Web"},
    {"id": "REQ-002", "customer": "Fatima Khan", "type": "PIN Reset", "status": "In Progress", "priority": "High", "time": "2m", "date": "2026-06-20", "channel": "Mobile"},
    {"id": "REQ-003", "customer": "Usman Malik", "type": "ATM Activation", "status": "Pending", "priority": "High", "time": "-", "date": "2026-06-20", "channel": "WhatsApp"},
    {"id": "REQ-004", "customer": "Sana Tariq", "type": "Statement", "status": "Resolved", "priority": "Medium", "time": "28s", "date": "2026-06-20", "channel": "Web"},
    {"id": "REQ-005", "customer": "Bilal Hassan", "type": "CNIC Update", "status": "Human Review", "priority": "High", "time": "15m", "date": "2026-06-20", "channel": "Mobile"},
    {"id": "REQ-006", "customer": "Zainab Ali", "type": "Letter", "status": "Resolved", "priority": "Medium", "time": "35s", "date": "2026-06-19", "channel": "Web"},
    {"id": "REQ-007", "customer": "Tariq Mehmood", "type": "Internet Banking", "status": "Pending", "priority": "High", "time": "-", "date": "2026-06-19", "channel": "IVR"},
    {"id": "REQ-008", "customer": "Hina Akram", "type": "Mobile Activation", "status": "Resolved", "priority": "Medium", "time": "52s", "date": "2026-06-19", "channel": "Web"},
    {"id": "REQ-009", "customer": "Omar Farooq", "type": "Card Unblock", "status": "In Progress", "priority": "Critical", "time": "5m", "date": "2026-06-19", "channel": "Mobile"},
    {"id": "REQ-010", "customer": "Ayesha Siddiqui", "type": "PIN Change", "status": "Resolved", "priority": "High", "time": "1m", "date": "2026-06-19", "channel": "Web"},
    {"id": "REQ-011", "customer": "Fahad Rizvi", "type": "Account Letter", "status": "Resolved", "priority": "Low", "time": "22s", "date": "2026-06-18", "channel": "Web"},
    {"id": "REQ-012", "customer": "Nadia Shah", "type": "CNIC Update", "status": "Resolved", "priority": "High", "time": "3m", "date": "2026-06-18", "channel": "Mobile"},
    {"id": "REQ-013", "customer": "Kamran Ali", "type": "Fraud Report", "status": "Human Review", "priority": "Critical", "time": "45m", "date": "2026-06-18", "channel": "Phone"},
    {"id": "REQ-014", "customer": "Rabia Anwar", "type": "Statement", "status": "Resolved", "priority": "Low", "time": "18s", "date": "2026-06-18", "channel": "Web"},
    {"id": "REQ-015", "customer": "Danish Iqbal", "type": "Mobile Activation", "status": "OTP Sent", "priority": "Medium", "time": "30s", "date": "2026-06-18", "channel": "WhatsApp"},
]


def seed_db():
    db = SessionLocal()
    if db.query(Case).count() > 0:
        db.close()
        return
    for c in SAMPLE_CASES:
        db.add(Case(
            id=c["id"], customer_id=c["id"], customer_name=c["customer"],
            type=c["type"], status=c["status"], priority=c["priority"],
            channel=c["channel"], time=c["time"], date=c["date"],
        ))
    db.commit()
    db.close()


@app.on_event("startup")
def on_start():
    init_db()
    seed_db()
    _get_jwks()


@app.get("/api/health")
def health():
    from backend.database import engine
    db_status = "connected"
    try:
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception:
        db_status = "disconnected"
    return {"status": "ok", "service": settings.APP_NAME, "version": settings.APP_VERSION, "database": db_status}


@app.get("/api")
def api_root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "endpoints": {
            "health": "GET /api/health",
            "auth_login": "POST /api/auth/login",
            "auth_register": "POST /api/auth/register",
            "auth_me": "GET /api/auth/me",
            "auth_refresh": "POST /api/auth/refresh",
            "dashboard_stats": "GET /api/dashboard/stats",
            "dashboard_cases": "GET /api/dashboard/cases",
            "classify": "POST /api/classify",
            "chat": "POST /api/chat",
            "document_verify": "POST /api/document/verify",
            "audit_log": "POST /api/audit/log",
            "audit_logs": "GET /api/audit/logs",
            "workflows": "GET /api/workflows",
            "customers": "GET /api/customers, POST /api/customers",
            "robots_status": "GET /api/robots/status",
            "robot_notification": "POST /api/robots/notification/send",
            "robot_document": "POST /api/robots/document/generate",
            "robot_audit_verify": "GET /api/robots/audit/verify",
            "smartfinance_status": "GET /api/smartfinance/status",
            "smartfinance_monitor": "POST /api/smartfinance/monitor",
            "smartfinance_fraud": "POST /api/smartfinance/fraud/analyze",
            "smartfinance_bill": "POST /api/smartfinance/bill/analyze",
            "smartfinance_recovery": "POST /api/smartfinance/recovery/analyze",
            "smartfinance_coach": "POST /api/smartfinance/coach/analyze",
            "smartfinance_communicate": "POST /api/smartfinance/communicate",
            "smartfinance_rpa_execute": "POST /api/smartfinance/rpa/execute",
            "smartfinance_rpa_comm": "POST /api/smartfinance/rpa/communicate",
            "smartfinance_rpa_report": "POST /api/smartfinance/rpa/report",
        },
    }


ui_dir = settings.ROOT_DIR / "ui"
static_dir = ui_dir / "dist"
if not static_dir.exists():
    static_dir = ui_dir
if static_dir.exists():
    app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="ui")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("backend.main:app", host="0.0.0.0", port=port, reload=True)
