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

from fastapi import APIRouter, HTTPException, Depends, Request, Body
from pydantic import ValidationError

from backend.auth import get_current_user
from backend.schemas import TransactionProcessRequest, TransactionProcessResponse
from backend.database import SessionLocal
from backend.models import FinanceCustomer, FinanceTransaction, gen_id

logger = logging.getLogger("smartbank.routers.smartfinance")
router = APIRouter(prefix="/api/smartfinance", tags=["SmartFinance Guardian"])

SYSTEM_ADMIN_ACCOUNT = "ADMIN-001"
SYSTEM_ADMIN_NAME = "SmartBank System Admin"

SIMULATION_MODE = True


# ─── Orchestrated SmartFinance Workflow ───
@router.post("/orchestrate")
async def orchestrate_guardian(
    request: Request,
    current_user=Depends(get_current_user),
) -> dict:
    """Full SmartFinance Guardian orchestration workflow (Monitor → Detect → Route → Resolve → Communicate)."""
    body = await request.json()
    customer_id = body.get("customer_id", "")
    profile = body.get("profile", {})
    
    result = {
        "customer_id": customer_id,
        "orchestration_id": str(uuid.uuid4())[:8].upper(),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "steps": [],
        "overall_status": "completed",
    }
    
    # STEP 1: Monitor customer financial profile
    from agents.financial_monitoring_agent import FinancialMonitoringAgent, CustomerFinancialProfile
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
    monitor_result = agent.analyze(customer_profile)
    result["steps"].append({
        "step": 1, "agent": "Financial Monitoring Agent",
        "action": "Analyzed customer financial profile",
        "problem_detected": monitor_result.problem_detected,
        "problem_type": monitor_result.problem_type,
        "severity": monitor_result.problem_severity,
        "risk_score": monitor_result.risk_score,
        "summary": monitor_result.analysis_summary,
    })
    if not monitor_result.problem_detected:
        result["steps"].append({"step": 2, "agent": "System", "action": "No problems detected", "problem_detected": False})
        result["overall_status"] = "healthy"
        return result
    
    problem_type = monitor_result.problem_type
    specialist_result = await _route_to_specialist(problem_type, customer_id, profile, customer_profile)
    if specialist_result:
        result["steps"].append(specialist_result["step_info"])
        # STEP 3: Generate communication
        try:
            comm_step = await _generate_communication(problem_type, customer_profile, specialist_result, profile)
            result["steps"].append(comm_step)
        except Exception as e:
            logger.warning(f"Communication failed: {e}")
    
    result["overall_status"] = f"problem_{problem_type.lower()}_handled"
    return result


# ─── Helper: Route to specialist agent ───
async def _route_to_specialist(problem_type, customer_id, profile, customer_profile):
    step_info = {"step": 2, "agent": f"{problem_type.title()} Agent", "action": "Analysis complete"}
    
    if problem_type == "FRAUD":
        from agents.fraud_prevention_agent import FraudPreventionAgent, Transaction
        td = profile.get("transaction_data", {})
        agent = FraudPreventionAgent()
        txn = Transaction(id=td.get("id", str(uuid.uuid4())), amount=float(td.get("amount", 0)),
            currency=td.get("currency", "PKR"), merchant=td.get("merchant", "Unknown"),
            category=td.get("category", "General"), timestamp=td.get("timestamp", ""),
            location=td.get("location", ""), is_international=bool(td.get("is_international", False)),
            is_online=bool(td.get("is_online", False)))
        history = [Transaction(id=h.get("id",""), amount=float(h.get("amount",0)),
            currency=h.get("currency","PKR"), merchant=h.get("merchant",""),
            category=h.get("category",""), timestamp=h.get("timestamp",""),
            location=h.get("location",""), is_international=bool(h.get("is_international",False)),
            is_online=bool(h.get("is_online",False))) for h in profile.get("transaction_history", [])[-50:]]
        result = agent.analyze(customer_id, txn, history, customer_profile.risk_score)
        step_info.update(risk_score=result.risk_score, risk_level=result.risk_level,
            recommendation=result.recommended_action)
        return {"result": result, "step_info": step_info}
    
    elif problem_type == "BILL":
        from agents.bill_protection_agent import BillProtectionAgent, Bill
        agent = BillProtectionAgent()
        bills = [Bill(id=b.get("id",""), biller_name=b.get("biller_name","Unknown"),
            category=b.get("category","Utilities"), amount=float(b.get("amount",0)),
            due_date=b.get("due_date",""), status=b.get("status","pending"),
            auto_pay=bool(b.get("auto_pay",False)), recurring=bool(b.get("recurring",False)))
            for b in profile.get("upcoming_bills", [])]
        result = agent.analyze(customer_id, customer_profile.account_balance, bills,
            profile.get("recurring_expenses", []), profile.get("income_schedule", []))
        step_info.update(at_risk=len(result.at_risk_bills), shortfall=result.projected_shortfall,
            recommendation=result.recommended_action)
        return {"result": result, "step_info": step_info}
    
    elif problem_type == "RECOVERY":
        from agents.transaction_recovery_agent import TransactionRecoveryAgent, FailedTransaction
        agent = TransactionRecoveryAgent()
        failed = [FailedTransaction(id=t.get("id",str(uuid.uuid4())), customer_id=customer_id,
            amount=float(t.get("amount",0)), currency=t.get("currency","PKR"),
            merchant=t.get("merchant",""), merchant_ref=t.get("merchant_ref",""),
            transaction_date=t.get("transaction_date",""),
            failure_reason=t.get("failure_reason",""),
            amount_deducted=bool(t.get("amount_deducted",True)),
            current_status=t.get("current_status","FAILED")) for t in profile.get("failed_transactions", [])]
        result = agent.analyze(customer_id, failed)
        step_info.update(recoverable=result.total_recoverable, method=result.recovery_method,
            recommendation=result.recommended_action)
        return {"result": result, "step_info": step_info}
    
    elif problem_type == "COACH":
        from agents.financial_coach_agent import FinancialCoachAgent, SpendingCategory
        agent = FinancialCoachAgent()
        categories = []
        for cat_name, cat_data in profile.get("spending_categories", {}).items():
            if isinstance(cat_data, dict):
                categories.append(SpendingCategory(name=cat_name, monthly_spend=float(cat_data.get("monthly_spend",0)),
                    percentage=float(cat_data.get("percentage",0)), trend=cat_data.get("trend","stable"),
                    is_subscription=bool(cat_data.get("is_subscription",False))))
            else:
                categories.append(SpendingCategory(name=cat_name, monthly_spend=float(cat_data), percentage=0, trend="stable", is_subscription=False))
        result = agent.analyze(customer_id, customer_profile.monthly_income,
            customer_profile.monthly_expenses, categories, customer_profile.account_balance,
            float(profile.get("subscription_spend", 0)))
        step_info.update(health_score=result.health_score, savings_potential=result.total_monthly_savings_potential,
            recommendation=result.analysis_summary)
        return {"result": result, "step_info": step_info}
    
    return None


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


# ─── AI Transaction Processing Workflow ───
@router.post("/transaction/process", response_model=TransactionProcessResponse)
async def process_transaction_workflow(
    body: TransactionProcessRequest,
    current_user=Depends(get_current_user),
) -> TransactionProcessResponse:
    """AI-powered transaction workflow.
    
    Two modes:
    1. Simple: Records a transaction with id + name + amount.
    2. Routing-based: If bank_routing_number is provided, looks up the customer
       and sends amount from the system admin account to the matched customer.
    """
    workflow_id = str(uuid.uuid4())[:8].upper()
    now = datetime.now(timezone.utc).isoformat()

    routing_val = (body.bank_routing_number or "").strip()
    acct_val = (body.account_number or body.transaction_id or "").strip()
    if routing_val and acct_val:
        # ── Routing-based transfer: admin → customer (dual verify: account# + routing#) ──
        db = SessionLocal()
        try:
            customer = db.query(FinanceCustomer).filter(
                FinanceCustomer.account_number == acct_val,
                FinanceCustomer.bank_routing_number == routing_val,
            ).first()

            if not customer:
                return TransactionProcessResponse(
                    success=False,
                    workflow_id=workflow_id,
                    transaction_type="routing_transfer",
                    message=f"Account '{acct_val}' + Routing '{routing_val}' not matched in database. Transaction REJECTED.",
                    timestamp=now,
                )

            # Determine sender account (default: system admin)
            sender_account = body.sender_account or SYSTEM_ADMIN_ACCOUNT
            sender = db.query(FinanceCustomer).filter(
                FinanceCustomer.account_number == sender_account
            ).first()

            # Auto-create system admin account if it doesn't exist
            if not sender:
                sender = FinanceCustomer(
                    customer_id=9999,
                    full_name=SYSTEM_ADMIN_NAME,
                    account_number=SYSTEM_ADMIN_ACCOUNT,
                    account_balance=1_000_000_000,
                    bank_routing_number="ADMIN-RTG-001",
                )
                db.add(sender)
                db.flush()
                logger.info(f"Created system admin account: {SYSTEM_ADMIN_ACCOUNT}")

            if sender.account_balance < body.amount:
                return TransactionProcessResponse(
                    success=False,
                    workflow_id=workflow_id,
                    transaction_type="routing_transfer",
                    message=(
                        f"Insufficient balance in sender account '{sender_account}'. "
                        f"Available: {sender.account_balance:,.2f}, Required: {body.amount:,.2f}"
                    ),
                    timestamp=now,
                )

            # Process transfer
            sender.account_balance -= body.amount
            customer.account_balance += body.amount

            txn = FinanceTransaction(
                id=gen_id(),
                sender_account=sender.account_number,
                receiver_account=customer.account_number,
                sender_name=sender.full_name,
                receiver_name=customer.full_name,
                amount=body.amount,
                type="routing_transfer",
                status="completed",
                description=body.description or (
                    f"AI Workflow transfer from {sender.full_name} "
                    f"to {customer.full_name} via {val}"
                ),
            )
            db.add(txn)
            db.commit()
            db.refresh(txn)

            logger.info(
                f"[AI Workflow {workflow_id}] Routing transfer: "
                f"{sender.full_name} -> {customer.full_name}, "
                f"Amount: {body.amount:,.2f}, Acct: {acct_val}, Routing: {routing_val}"
            )

            return TransactionProcessResponse(
                success=True,
                workflow_id=workflow_id,
                transaction_type="routing_transfer",
                transaction_id=txn.id,
                sender_name=sender.full_name,
                receiver_name=customer.full_name,
                receiver_account=customer.account_number,
                amount=body.amount,
                routing_verified=True,
                message=(
                    f"✅ Routing transfer successful! "
                    f"{body.amount:,.2f} sent from {sender.full_name} "
                    f"to {customer.full_name} (acct: {customer.account_number})."
                ),
                timestamp=now,
            )
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            logger.error(f"[AI Workflow {workflow_id}] Routing transfer failed: {e}")
            return TransactionProcessResponse(
                success=False,
                workflow_id=workflow_id,
                transaction_type="routing_transfer",
                message=f"Transaction failed: {str(e)}",
                timestamp=now,
            )
        finally:
            db.close()
    else:
        # ── Simple transaction record ──
        db = SessionLocal()
        try:
            txn = FinanceTransaction(
                id=gen_id(),
                sender_account=body.sender_account or "WALK-IN",
                receiver_account=body.transaction_id,
                sender_name=SYSTEM_ADMIN_NAME,
                receiver_name=body.customer_name,
                amount=body.amount,
                type="simple_entry",
                status="completed",
                description=body.description or (
                    f"AI Workflow entry: {body.customer_name} - {body.transaction_id}"
                ),
            )
            db.add(txn)
            db.commit()
            db.refresh(txn)

            logger.info(
                f"[AI Workflow {workflow_id}] Simple transaction: "
                f"{body.customer_name}, Amount: {body.amount:,.2f}"
            )

            return TransactionProcessResponse(
                success=True,
                workflow_id=workflow_id,
                transaction_type="simple_entry",
                transaction_id=txn.id,
                receiver_name=body.customer_name,
                amount=body.amount,
                message=f"Transaction recorded: {body.customer_name}, Amount: {body.amount:,.2f}",
                timestamp=now,
            )
        except Exception as e:
            db.rollback()
            logger.error(f"[AI Workflow {workflow_id}] Simple transaction failed: {e}")
            return TransactionProcessResponse(
                success=False,
                workflow_id=workflow_id,
                transaction_type="simple_entry",
                message=f"Transaction failed: {str(e)}",
                timestamp=now,
            )
        finally:
            db.close()


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
            {"name": "Transaction Workflow Agent", "status": "Online"},
        ],
        "rpa_robots": [
            {"name": "Transaction Processing Bot", "status": "Online", "mode": "Simulation" if SIMULATION_MODE else "Live"},
            {"name": "Communication Bot", "status": "Online", "mode": "Simulation" if SIMULATION_MODE else "Live"},
            {"name": "Reporting Bot", "status": "Online", "mode": "Simulation" if SIMULATION_MODE else "Live"},
        ],
        "simulation_mode": SIMULATION_MODE,
    }
