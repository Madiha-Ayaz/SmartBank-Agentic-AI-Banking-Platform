"""
SmartFinance Dummy Banking API

A realistic banking backend simulation for the SmartFinance AI platform.
Integrates with UiPath Maestro BPMN workflows, AI Guardian Agents, and RPA robots.

Run: uvicorn banking_api.main:app --reload --port 8001
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from banking_api.config import settings
from banking_api.database import init_db, SessionLocal
from banking_api.seed_data import seed_database

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)
logger = logging.getLogger("banking_api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"{settings.APP_NAME} v{settings.APP_VERSION} starting...")
    init_db()
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()
    yield
    logger.info("Banking API shutting down...")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "Dummy Banking API for SmartFinance AI platform. "
        "Simulates core banking operations including customer management, "
        "account balances, transaction processing, fraud detection, "
        "payment processing, refunds, card management, notifications, "
        "and financial health analysis."
        "\n\n"
        "## Integration\n"
        "- UiPath Maestro BPMN HTTP/API Tasks\n"
        "- AI Financial Guardian Agents\n"
        "- RPA Robots\n"
        "- Frontend Dashboard Applications"
    ),
    contact={
        "name": "SmartFinance AI",
        "url": "https://smartbank.ai",
    },
    license_info={
        "name": "Apache 2.0",
    },
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
from banking_api.routers import (
    customers,
    accounts,
    transactions,
    fraud,
    payments,
    refunds,
    cards,
    notifications,
    financial_health,
)

app.include_router(customers.router)
app.include_router(accounts.router)
app.include_router(transactions.router)
app.include_router(fraud.router)
app.include_router(payments.router)
app.include_router(refunds.router)
app.include_router(cards.router)
app.include_router(notifications.router)
app.include_router(financial_health.router)


@app.get("/", tags=["Health"])
def root():
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
        "endpoints": {
            "customers": "GET /api/customers/{customer_id}",
            "accounts": "GET /api/accounts/{account_id}/balance",
            "transactions": "GET /api/transactions/{customer_id}",
            "fraud_check": "POST /api/fraud/check",
            "fraud_cases": "GET /api/fraud/cases/{customer_id}",
            "payment_process": "POST /api/payment/process",
            "refund_create": "POST /api/refund/create",
            "card_block": "POST /api/card/block",
            "card_unblock": "POST /api/card/unblock",
            "notification_send": "POST /api/notification/send",
            "financial_health": "GET /api/financial-health/{customer_id}",
        },
    }


@app.get("/api/health", tags=["Health"])
def health_check():
    return {"status": "ok", "service": settings.APP_NAME, "version": settings.APP_VERSION}


if __name__ == "__main__":
    import uvicorn
    port = 8001
    logger.info(f"Starting Banking API on port {port}")
    uvicorn.run("banking_api.main:app", host="0.0.0.0", port=port, reload=True)
