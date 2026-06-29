from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException

from agents.loan_agent.conversation_agent import LoanConversationAgent
from backend.database import SessionLocal
from backend.models import LoanApplication, LoanAgreement
from backend.schemas import (
    LoanChatRequest,
    LoanChatResponse,
    LoanApplicationResponse,
    LoanAgreementResponse,
    LoanAcceptTermsRequest,
    LoanAcceptTermsResponse,
)

logger = logging.getLogger("smartbank.routers.loan")
router = APIRouter(prefix="/api/loan", tags=["Loan"])

agent = LoanConversationAgent()


@router.post("/chat", response_model=LoanChatResponse)
async def loan_chat(body: LoanChatRequest) -> LoanChatResponse:
    if not body.message:
        raise HTTPException(status_code=400, detail="message is required")
    try:
        result = agent.process_message(
            message=body.message,
            application_id=body.application_id,
            language=body.language or "en",
        )
        return LoanChatResponse(
            text=result["text"],
            application_id=result["application_id"],
            current_step=result["current_step"],
            data_collected=result["data_collected"],
            completed=result["completed"],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/accept-terms", response_model=LoanAcceptTermsResponse)
async def accept_terms(body: LoanAcceptTermsRequest) -> LoanAcceptTermsResponse:
    if not body.application_id:
        raise HTTPException(status_code=400, detail="application_id is required")
    try:
        if body.accepted:
            result = agent.accept_terms(body.application_id)
            if result["success"]:
                agreement_data = result.get("agreement")
                agreement_resp = None
                if agreement_data:
                    agreement_resp = LoanAgreementResponse(
                        id=agreement_data["id"],
                        loan_application_id=agreement_data["loan_application_id"],
                        agreement_text=agreement_data["agreement_text"],
                        payment_schedule=agreement_data["payment_schedule"],
                        created_at=agreement_data["created_at"],
                    )
                return LoanAcceptTermsResponse(
                    success=True,
                    message=result["message"],
                    agreement=agreement_resp,
                )
            return LoanAcceptTermsResponse(success=False, message=result["message"])
        else:
            db = SessionLocal()
            try:
                application = db.query(LoanApplication).filter(
                    LoanApplication.id == body.application_id
                ).first()
                if application:
                    application.status = "rejected"
                    application.current_step = "rejected"
                    db.commit()
            finally:
                db.close()
            return LoanAcceptTermsResponse(
                success=False,
                message="You have declined the loan terms. Your application has been closed.",
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/application/{application_id}", response_model=LoanApplicationResponse)
async def get_application(application_id: str) -> LoanApplicationResponse:
    db = SessionLocal()
    try:
        app = db.query(LoanApplication).filter(LoanApplication.id == application_id).first()
        if not app:
            raise HTTPException(status_code=404, detail="Application not found")
        return LoanApplicationResponse(
            id=app.id,
            status=app.status,
            current_step=app.current_step,
            full_name=app.full_name,
            cnic=app.cnic,
            phone=app.phone,
            email=app.email,
            employment_type=app.employment_type,
            loan_amount=app.loan_amount,
            loan_purpose=app.loan_purpose,
            repayment_duration_months=app.repayment_duration_months,
            risk_level=app.risk_level,
            credit_score=app.credit_score,
            interest_rate=app.interest_rate,
            monthly_payment=app.monthly_payment,
            decision_reason=app.decision_reason,
            terms_accepted=app.terms_accepted or False,
            created_at=app.created_at.isoformat() if app.created_at else "",
            updated_at=app.updated_at.isoformat() if app.updated_at else "",
        )
    finally:
        db.close()


@router.get("/agreement/{application_id}", response_model=LoanAgreementResponse)
async def get_agreement(application_id: str) -> LoanAgreementResponse:
    db = SessionLocal()
    try:
        agreement = db.query(LoanAgreement).filter(
            LoanAgreement.loan_application_id == application_id
        ).first()
        if not agreement:
            raise HTTPException(status_code=404, detail="Agreement not found")
        return LoanAgreementResponse(
            id=agreement.id,
            loan_application_id=agreement.loan_application_id,
            agreement_text=agreement.agreement_text or "",
            payment_schedule=agreement.payment_schedule or [],
            created_at=agreement.created_at.isoformat() if agreement.created_at else "",
        )
    finally:
        db.close()


@router.get("/applications", response_model=list[LoanApplicationResponse])
async def list_applications():
    db = SessionLocal()
    try:
        apps = db.query(LoanApplication).order_by(LoanApplication.created_at.desc()).limit(50).all()
        return [
            LoanApplicationResponse(
                id=a.id,
                status=a.status,
                current_step=a.current_step,
                full_name=a.full_name,
                cnic=a.cnic,
                phone=a.phone,
                email=a.email,
                employment_type=a.employment_type,
                loan_amount=a.loan_amount,
                loan_purpose=a.loan_purpose,
                repayment_duration_months=a.repayment_duration_months,
                risk_level=a.risk_level,
                credit_score=a.credit_score,
                interest_rate=a.interest_rate,
                monthly_payment=a.monthly_payment,
                decision_reason=a.decision_reason,
                terms_accepted=a.terms_accepted or False,
                created_at=a.created_at.isoformat() if a.created_at else "",
                updated_at=a.updated_at.isoformat() if a.updated_at else "",
            )
            for a in apps
        ]
    finally:
        db.close()
