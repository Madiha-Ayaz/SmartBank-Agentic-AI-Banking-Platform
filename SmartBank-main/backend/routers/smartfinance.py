"""
SmartFinance AI Guardian — Backend API Router

Exposes endpoints for:
- Financial Monitoring & Analysis
- Fraud Prevention
- Bill Protection
- Transaction Recovery
- Financial Coaching
- AI Communication
- RPA Transaction Processing
"""

from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from fastapi import APIRouter, HTTPException, Depends, Request

from backend.auth import get_current_user

logger = logging.getLogger("smartbank.routers.smartfinance")
router = APIRouter(prefix="/api/smartfinance", tags=["SmartFinance Guardian"])

SIMULATION_MODE = True


@router.post("/monitor")
async def monitor_customer(
    request: Request,
    current_user=Depends(get_current_user),
) -> dict:
    body = await request.json()
    customer_id = body.get("customer_id", "")
    profile = body.get("profile", {})

    from agents.financial_monitoring_agent import (
        FinancialMonitoringAgent,
        CustomerFinancialProfile,
    )

    agent = FinancialMonitoringAgent()
    customer_profile = CustomerFinancialProfile(
        customer_id=customer_id,
        customer_name=profile.get("customer_name", "Unknown"),
        account_balance=float(profile.get("account_balance", 0)),
        monthly_income=float(profile.get("monthly_income", 0)),
        monthly_expenses=float(profile.get("monthly_expenses", 0)),
        transaction_count_30d=int(profile.get("transaction_count_30d", 0)),
        unusual_transactions_30d=int(profile.get("unusual_transactions_30d", 0)),
        failed_payments_30d=int(profile.get("failed_payments_30d", 0)),
        fraud_alerts_30d=int(profile.get("fraud_alerts_30d", 0)),
        risk_score=float(profile.get("risk_score", 0)),
        savings_rate=float(profile.get("savings_rate", 0)),
        bill_payment_reliability=float(profile.get("bill_payment_reliability", 1.0)),
        spending_categories=profile.get("spending_categories", {}),
        upcoming_bills=profile.get("upcoming_bills", []),
        recent_transactions=profile.get("recent_transactions", []),
    )

    result = agent.analyze(customer_profile)
    return {
        "success": True,
        "customer_id": result.customer_id,
        "problem_detected": result.problem_detected,
        "problem_type": result.problem_type,
        "problem_severity": result.problem_severity,
        "risk_score": result.risk_score,
        "confidence": result.confidence,
        "summary": result.analysis_summary,
        "recommendation": result.recommendation,
        "timestamp": result.timestamp,
    }


@router.post("/fraud/analyze")
async def analyze_fraud(
    request: Request,
    current_user=Depends(get_current_user),
) -> dict:
    body = await request.json()
    customer_id = body.get("customer_id", "")
    transaction_data = body.get("transaction", {})
    history_data = body.get("transaction_history", [])

    from agents.fraud_prevention_agent import FraudPreventionAgent, Transaction

    agent = FraudPreventionAgent()
    txn = Transaction(
        id=transaction_data.get("id", str(uuid.uuid4())),
        amount=float(transaction_data.get("amount", 0)),
        currency=transaction_data.get("currency", "PKR"),
        merchant=transaction_data.get("merchant", "Unknown"),
        category=transaction_data.get("category", "General"),
        timestamp=transaction_data.get("timestamp", datetime.now(timezone.utc).isoformat()),
        location=transaction_data.get("location", "Unknown"),
        is_international=bool(transaction_data.get("is_international", False)),
        is_online=bool(transaction_data.get("is_online", False)),
    )

    history = [
        Transaction(
            id=h.get("id", ""),
            amount=float(h.get("amount", 0)),
            currency=h.get("currency", "PKR"),
            merchant=h.get("merchant", ""),
            category=h.get("category", ""),
            timestamp=h.get("timestamp", ""),
            location=h.get("location", ""),
            is_international=bool(h.get("is_international", False)),
            is_online=bool(h.get("is_online", False)),
        )
        for h in history_data[-50:]
    ]

    result = agent.analyze(
        customer_id=customer_id,
        transaction=txn,
        historical_transactions=history,
        customer_risk_score=float(body.get("customer_risk_score", 0)),
    )

    return {
        "success": True,
        "customer_id": result.customer_id,
        "risk_score": result.risk_score,
        "risk_level": result.risk_level,
        "suspicious_indicators": result.suspicious_indicators,
        "recommended_action": result.recommended_action,
        "requires_human_review": result.requires_human_review,
        "summary": result.analysis_summary,
        "confidence": result.confidence,
        "timestamp": result.timestamp,
    }


@router.post("/bill/analyze")
async def analyze_bills(
    request: Request,
    current_user=Depends(get_current_user),
) -> dict:
    body = await request.json()
    customer_id = body.get("customer_id", "")
    balance = float(body.get("account_balance", 0))
    bills_data = body.get("upcoming_bills", [])

    from agents.bill_protection_agent import BillProtectionAgent, Bill

    agent = BillProtectionAgent()
    bills = [
        Bill(
            id=b.get("id", str(uuid.uuid4())),
            biller_name=b.get("biller_name", "Unknown"),
            category=b.get("category", "Other"),
            amount=float(b.get("amount", 0)),
            due_date=b.get("due_date", ""),
            status=b.get("status", "pending"),
            auto_pay=bool(b.get("auto_pay", False)),
            recurring=bool(b.get("recurring", True)),
        )
        for b in bills_data
    ]

    result = agent.analyze(
        customer_id=customer_id,
        account_balance=balance,
        upcoming_bills=bills,
        recurring_expenses=body.get("recurring_expenses", []),
        income_schedule=body.get("income_schedule", []),
    )

    return {
        "success": True,
        "customer_id": result.customer_id,
        "at_risk_bills": result.at_risk_bills,
        "total_at_risk_amount": result.total_at_risk_amount,
        "current_balance": result.current_balance,
        "projected_shortfall": result.projected_shortfall,
        "recommended_action": result.recommended_action,
        "requires_human_approval": result.requires_human_approval,
        "summary": result.analysis_summary,
        "confidence": result.confidence,
        "timestamp": result.timestamp,
    }


@router.post("/recovery/analyze")
async def analyze_recovery(
    request: Request,
    current_user=Depends(get_current_user),
) -> dict:
    body = await request.json()
    customer_id = body.get("customer_id", "")
    failed_txns = body.get("failed_transactions", [])

    from agents.transaction_recovery_agent import TransactionRecoveryAgent, FailedTransaction

    agent = TransactionRecoveryAgent()
    transactions = [
        FailedTransaction(
            id=t.get("id", str(uuid.uuid4())),
            customer_id=customer_id,
            amount=float(t.get("amount", 0)),
            currency=t.get("currency", "PKR"),
            merchant=t.get("merchant", "Unknown"),
            merchant_ref=t.get("merchant_ref", ""),
            transaction_date=t.get("transaction_date", ""),
            failure_reason=t.get("failure_reason", "Unknown"),
            amount_deducted=bool(t.get("amount_deducted", True)),
            current_status=t.get("current_status", "failed"),
        )
        for t in failed_txns
    ]

    result = agent.analyze(
        customer_id=customer_id,
        failed_transactions=transactions,
    )

    return {
        "success": True,
        "customer_id": result.customer_id,
        "failed_transactions": result.failed_transactions,
        "total_recoverable": result.total_recoverable,
        "recovery_method": result.recovery_method,
        "auto_recoverable": result.auto_recoverable,
        "requires_human_review": result.requires_human_review,
        "recommended_action": result.recommended_action,
        "summary": result.analysis_summary,
        "confidence": result.confidence,
        "timestamp": result.timestamp,
    }


@router.post("/coach/analyze")
async def analyze_financial_health(
    request: Request,
    current_user=Depends(get_current_user),
) -> dict:
    body = await request.json()
    customer_id = body.get("customer_id", "")
    income = float(body.get("monthly_income", 0))
    expenses = float(body.get("monthly_expenses", 0))
    savings = float(body.get("savings_balance", 0))
    subscription_spend = float(body.get("subscription_spend", 0))
    categories_data = body.get("spending_categories", [])

    from agents.financial_coach_agent import FinancialCoachAgent, SpendingCategory

    agent = FinancialCoachAgent()
    categories = [
        SpendingCategory(
            name=c.get("name", "Unknown"),
            monthly_spend=float(c.get("monthly_spend", 0)),
            percentage=float(c.get("percentage", 0)),
            trend=c.get("trend", "stable"),
            is_subscription=bool(c.get("is_subscription", False)),
        )
        for c in categories_data
    ]

    result = agent.analyze(
        customer_id=customer_id,
        monthly_income=income,
        monthly_expenses=expenses,
        categories=categories,
        savings_balance=savings,
        subscription_spend=subscription_spend,
    )

    return {
        "success": True,
        "customer_id": result.customer_id,
        "health_score": result.health_score,
        "spending_analysis": result.spending_analysis,
        "saving_opportunities": result.saving_opportunities,
        "budget_recommendations": result.budget_recommendations,
        "total_monthly_savings_potential": result.total_monthly_savings_potential,
        "requires_human_review": result.requires_human_review,
        "summary": result.analysis_summary,
        "confidence": result.confidence,
        "timestamp": result.timestamp,
    }


@router.post("/communicate")
async def generate_communication(
    request: Request,
    current_user=Depends(get_current_user),
) -> dict:
    body = await request.json()
    problem_type = body.get("problem_type", "RESOLVED")
    customer_name = body.get("customer_name", "Valued Customer")
    params = body.get("params", {})

    from agents.communication_agent import AICommunicationAgent

    agent = AICommunicationAgent()
    message = agent.generate_message(
        problem_type=problem_type,
        customer_name=customer_name,
        params=params,
    )

    return {
        "success": True,
        "problem_type": message.problem_type,
        "subject": message.subject,
        "body": message.body,
        "sms_text": message.sms_text,
        "push_text": message.push_text,
        "whatsapp_text": message.whatsapp_text,
        "tone": message.tone,
        "urgency": message.urgency,
        "timestamp": message.timestamp,
    }


@router.post("/rpa/execute")
async def execute_rpa_action(
    request: Request,
    current_user=Depends(get_current_user),
) -> dict:
    body = await request.json()

    from robots.transaction_processing_bot import TransactionProcessingRobot, ActionRequest

    action_req = ActionRequest(
        action_id=body.get("action_id", str(uuid.uuid4())),
        case_id=body.get("case_id", ""),
        customer_id=body.get("customer_id", ""),
        action_type=body.get("action_type", ""),
        parameters=body.get("parameters", {}),
        source=body.get("source", "SmartFinance API"),
        approval_ref=body.get("approval_ref"),
    )

    robot = TransactionProcessingRobot()
    result = robot.execute(action_req)

    return {
        "success": result.status == "SUCCESS",
        "action_id": result.action_id,
        "status": result.status,
        "message": result.message,
        "transaction_ref": result.transaction_ref,
        "details": result.details,
    }


@router.post("/rpa/communicate")
async def send_communication(
    request: Request,
    current_user=Depends(get_current_user),
) -> dict:
    body = await request.json()

    from robots.communication_bot import CommunicationBot, CommunicationRequest

    comm_req = CommunicationRequest(
        customer_id=body.get("customer_id", ""),
        case_id=body.get("case_id", ""),
        channel=body.get("channel", "sms"),
        template=body.get("template", "resolution_complete"),
        recipient=body.get("recipient", ""),
        params=body.get("params", {}),
        priority=body.get("priority", "NORMAL"),
    )

    bot = CommunicationBot()
    result = bot.send(comm_req)

    return {
        "success": result.status == "SENT",
        "request_id": result.request_id,
        "channel": result.channel,
        "status": result.status,
        "message": result.message,
        "delivery_ref": result.delivery_ref,
    }


@router.post("/rpa/report")
async def generate_report(
    request: Request,
    current_user=Depends(get_current_user),
) -> dict:
    body = await request.json()

    from robots.reporting_bot import ReportingBot, ReportRequest

    report_req = ReportRequest(
        case_id=body.get("case_id", ""),
        report_type=body.get("report_type", "resolution_summary"),
        customer_id=body.get("customer_id", ""),
        data=body.get("data", {}),
        include_pii=bool(body.get("include_pii", False)),
    )

    bot = ReportingBot()
    result = bot.generate(report_req)

    return {
        "success": result.status == "SUCCESS",
        "report_id": result.report_id,
        "report_type": result.report_type,
        "status": result.status,
        "message": result.message,
        "report_path": result.report_path,
        "entries_count": result.entries_count,
    }


@router.get("/status")
async def guardian_status(current_user=Depends(get_current_user)) -> dict:
    return {
        "service": "SmartFinance AI Guardian",
        "version": "1.0.0",
        "status": "Active",
        "ai_agents": [
            {"name": "Financial Monitoring Agent", "status": "Online"},
            {"name": "Fraud Prevention Agent", "status": "Online"},
            {"name": "Bill Protection Agent", "status": "Online"},
            {"name": "Transaction Recovery Agent", "status": "Online"},
            {"name": "Financial Coach Agent", "status": "Online"},
            {"name": "AI Communication Agent", "status": "Online"},
        ],
        "rpa_robots": [
            {"name": "Transaction Processing Bot", "status": "Online", "mode": "Simulation" if SIMULATION_MODE else "Live"},
            {"name": "Communication Bot", "status": "Online", "mode": "Simulation" if SIMULATION_MODE else "Live"},
            {"name": "Reporting Bot", "status": "Online", "mode": "Simulation" if SIMULATION_MODE else "Live"},
        ],
        "simulation_mode": SIMULATION_MODE,
    }
