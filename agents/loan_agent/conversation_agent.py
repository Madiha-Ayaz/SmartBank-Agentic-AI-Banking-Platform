import json
import logging
from datetime import datetime, timezone
from typing import Optional

from agents.loan_agent.llm_client import call_llm, extract_json
from agents.loan_agent.risk_assessment import calculate_risk, decide_loan
from agents.loan_agent.prompts import (
    PROMPT_GREETING,
    PROMPT_COLLECT_NAME,
    PROMPT_COLLECT_CNIC,
    PROMPT_COLLECT_PHONE,
    PROMPT_COLLECT_EMAIL,
    PROMPT_COLLECT_PROFESSION,
    PROMPT_COLLECT_EMPLOYMENT,
    PROMPT_COLLECT_BUSINESS,
    PROMPT_COLLECT_LOAN_REQUIREMENT,
    PROMPT_DOCUMENT_REQUEST,
    PROMPT_RISK_ASSESSMENT,
    PROMPT_APPROVAL,
    PROMPT_REJECTION,
)
from backend.database import SessionLocal
from backend.models import LoanApplication, LoanAgreement

logger = logging.getLogger("smartbank.loan_agent.conversation")

STEP_PROMPTS = {
    "greeting": PROMPT_GREETING,
    "collecting_name": PROMPT_COLLECT_NAME,
    "collecting_cnic": PROMPT_COLLECT_CNIC,
    "collecting_phone": PROMPT_COLLECT_PHONE,
    "collecting_email": PROMPT_COLLECT_EMAIL,
    "collecting_profession": PROMPT_COLLECT_PROFESSION,
    "collecting_employment_details": PROMPT_COLLECT_EMPLOYMENT,
    "collecting_business_details": PROMPT_COLLECT_BUSINESS,
    "collecting_loan_requirement": PROMPT_COLLECT_LOAN_REQUIREMENT,
    "document_verification": PROMPT_DOCUMENT_REQUEST,
    "risk_assessment": PROMPT_RISK_ASSESSMENT,
}


class LoanConversationAgent:

    FALLBACK_MESSAGE = {
        "greeting": "Welcome to SmartBank Loan Assistant! I'm here to help you apply for a loan. I'll collect some information, check your eligibility, and guide you through the process.\n\nTo start, could you please tell me your full name?",
        "collecting_name": "Thank you! Could you please provide your full name so I can begin your application?",
        "collecting_cnic": "Please provide your CNIC/Identity number (13 digits without dashes or with dashes).",
        "collecting_phone": "Thank you! What is your phone number so we can contact you?",
        "collecting_email": "What is your email address?",
        "collecting_profession": "Are you currently employed, self-employed, or running your own business?",
        "collecting_employment_details": "Which company do you work for?",
        "collecting_business_details": "What type of business do you own?",
        "collecting_loan_requirement": "How much loan amount do you need?",
        "document_verification": "Please upload your documents for verification:\n1. CNIC copy (front and back)\n2. Salary slip / Business proof\n3. Bank statement (last 6 months)",
        "risk_assessment": "Thank you! I'm now reviewing your application to check your eligibility. This will just take a moment...",
    }

    def __init__(self):
        self._conversation_history = []

    def process_message(
        self, message: str, application_id: Optional[str] = None, language: str = "en"
    ) -> dict:
        db = SessionLocal()
        try:
            application = self._get_or_create_application(db, application_id)
            current_step = application.current_step or "greeting"

            if current_step == "greeting" and message.strip():
                current_step = "collecting_name"
                application.current_step = current_step

            extracted, next_step, reply = self._handle_step(
                message, current_step, application
            )

            application = self._update_application(
                db, application, extracted, next_step, reply, message
            )

            if next_step in ("terms_acceptance", "rejected", "agreement_generated", "completed"):
                pass

            if next_step == "risk_assessment":
                risk_result = calculate_risk({
                    "data_collected": application.conversation_history[-1].get("data_collected", {})
                    if application.conversation_history else {}
                })
                decision = decide_loan(risk_result, {
                    "data_collected": application.conversation_history[-1].get("data_collected", {})
                    if application.conversation_history else {}
                })

                application.income_stability_score = risk_result["income_stability_score"]
                application.debt_ratio = risk_result["debt_ratio"]
                application.repayment_capability_score = risk_result["repayment_capability_score"]
                application.credit_score = risk_result["credit_score"]
                application.risk_level = risk_result["risk_level"]
                application.risk_factors = risk_result["risk_factors"]

                if decision["approved"]:
                    application.status = "approved"
                    application.decision_reason = decision["decision_reason"]
                    application.interest_rate = decision["interest_rate"]
                    application.monthly_payment = decision["monthly_payment"]
                    application.total_payment = decision["total_payment"]
                    application.late_payment_charge_rate = decision["late_payment_charge_rate"]
                    application.improvement_suggestions = decision.get("improvement_suggestions")

                    loan_amount = application.loan_amount or 0
                    duration = application.repayment_duration_months or 12
                    terms_text = (
                        f"Congratulations {application.full_name}! Your loan application has been approved! 🎉\n\n"
                        f"Here are your loan terms:\n"
                        f"• Loan Amount: ${loan_amount:,.2f}\n"
                        f"• Interest Rate: {decision['interest_rate']}% per year\n"
                        f"• Monthly Payment: ${decision['monthly_payment']:,.2f}\n"
                        f"• Total Repayment: ${decision['total_payment']:,.2f}\n"
                        f"• Duration: {duration} months\n"
                        f"• Late Payment Charge: {decision['late_payment_charge_rate']}% of missed amount\n\n"
                        f"Do you accept these terms and conditions?"
                    )
                    reply = terms_text
                    application.current_step = "terms_acceptance"
                else:
                    application.status = "rejected"
                    application.decision_reason = decision["decision_reason"]
                    application.improvement_suggestions = decision.get("improvement_suggestions")
                    improvement_text = ""
                    if decision.get("improvement_suggestions"):
                        improvement_text = "\n\nSuggestions to improve:\n" + "\n".join(
                            f"• {s}" for s in decision["improvement_suggestions"]
                        )
                    reply = (
                        f"Unfortunately, your application does not meet our current lending criteria. "
                        f"{decision['decision_reason']}{improvement_text}\n\n"
                        f"We encourage you to work on these areas and reapply in the future."
                    )
                    application.current_step = "rejected"

                db.commit()

            if next_step == "document_verification":
                reply = (
                    f"Thank you for providing all the information, {application.full_name}! "
                    f"Your profile has been created successfully.\n\n"
                    f"Now, I need to verify some documents. Please upload:\n"
                    f"1. Your CNIC copy (front and back)\n"
                    f"2. Your {'salary slip' if application.employment_type == 'employee' else 'business registration/proof'}\n"
                    f"3. Your last 6 months bank statement\n\n"
                    f"You can upload these files through the upload button below."
                )

            if next_step == "agree_generated":
                agreement = self._generate_agreement(db, application)
                reply = (
                    f"Your loan agreement has been generated! You can view and download it below.\n\n"
                    f"Thank you for choosing SmartBank, {application.full_name}! "
                    f"We'll monitor your repayment journey and send you reminders."
                )

            data_collected = self._get_latest_data(application)

            return {
                "text": reply,
                "application_id": application.id,
                "current_step": application.current_step,
                "data_collected": data_collected,
                "completed": application.current_step in ("agreement_generated", "completed"),
            }
        finally:
            db.close()

    def _get_or_create_application(self, db, application_id: Optional[str]) -> LoanApplication:
        if application_id:
            app = db.query(LoanApplication).filter(LoanApplication.id == application_id).first()
            if app:
                return app
        application = LoanApplication(
            current_step="greeting",
            conversation_history=[],
        )
        db.add(application)
        db.commit()
        db.refresh(application)
        return application

    def _handle_step(self, message: str, step: str, application: LoanApplication):
        if step in STEP_PROMPTS and message.strip():
            system_prompt = STEP_PROMPTS[step]
            all_data = self._get_latest_data(application)
            system_prompt = system_prompt.replace("{data}", json.dumps(all_data))
            system_prompt = system_prompt.replace("{step}", step)

            messages = []
            for entry in (application.conversation_history or []):
                if entry.get("user_message"):
                    messages.append({"role": "user", "content": entry["user_message"]})
                if entry.get("assistant_reply"):
                    messages.append({"role": "assistant", "content": entry["assistant_reply"]})

            if message.strip():
                messages.append({"role": "user", "content": message})

            llm_reply = call_llm(messages, system_prompt=system_prompt)
            parsed = extract_json(llm_reply)

            if parsed:
                reply_text = parsed.get("text", llm_reply)
                next_step = parsed.get("next_step", step)
                extracted = parsed.get("extracted_data", {})
            else:
                reply_text = llm_reply if llm_reply else self.FALLBACK_MESSAGE.get(step, "")
                next_step = self._auto_next_step(step)
                extracted = self._auto_extract(message, step)

            return extracted, next_step, reply_text

        step_order = [
            "greeting", "collecting_name", "collecting_cnic", "collecting_phone",
            "collecting_email", "collecting_profession", "collecting_employment_details",
            "collecting_business_details", "collecting_loan_requirement",
            "document_verification", "risk_assessment",
        ]
        if step in step_order:
            idx = step_order.index(step)
            next_step = step_order[idx + 1] if idx + 1 < len(step_order) else step
        else:
            next_step = step

        return {}, next_step, self.FALLBACK_MESSAGE.get(step, "How can I help you with your loan application?")

    def _auto_next_step(self, step: str) -> str:
        mapping = {
            "greeting": "collecting_name",
            "collecting_name": "collecting_cnic",
            "collecting_cnic": "collecting_phone",
            "collecting_phone": "collecting_email",
            "collecting_email": "collecting_profession",
            "collecting_profession": "collecting_employment_details",
            "collecting_employment_details": "collecting_loan_requirement",
            "collecting_business_details": "collecting_loan_requirement",
            "collecting_loan_requirement": "document_verification",
            "document_verification": "risk_assessment",
        }
        return mapping.get(step, step)

    def _auto_extract(self, message: str, step: str) -> dict:
        msg_lower = message.lower()
        if step == "collecting_name":
            return {"full_name": message.strip()}
        elif step == "collecting_cnic":
            import re
            digits = re.sub(r"\D", "", message)
            return {"cnic": digits if len(digits) >= 13 else message.strip()}
        elif step == "collecting_phone":
            import re
            digits = re.sub(r"\D", "", message)
            return {"phone": digits if len(digits) >= 10 else message.strip()}
        elif step == "collecting_email":
            return {"email": message.strip()}
        elif step == "collecting_profession":
            if any(w in msg_lower for w in ["employ", "job", "work for", "salary"]):
                return {"employment_type": "employee"}
            elif any(w in msg_lower for w in ["business", "own", "shop", "company", "owner"]):
                return {"employment_type": "business_owner"}
            elif any(w in msg_lower for w in ["freelance", "self", "independent", "contract"]):
                return {"employment_type": "self_employed"}
            return {"employment_type": "employee"}
        elif step == "collecting_employment_details":
            return self._auto_extract_employment(message)
        elif step == "collecting_business_details":
            return self._auto_extract_business(message)
        elif step == "collecting_loan_requirement":
            return self._auto_extract_loan(message)
        return {}

    def _auto_extract_employment(self, message: str) -> dict:
        import re
        result = {}
        salary_match = re.search(r"(\d[\d,]*\.?\d*)\s*(k|thousand|million)?\s*(per month|monthly|/month)", message, re.IGNORECASE)
        if salary_match:
            val = float(salary_match.group(1).replace(",", ""))
            multiplier = salary_match.group(2)
            if multiplier and "k" in multiplier.lower():
                val *= 1000
            elif multiplier and "million" in multiplier.lower():
                val *= 1000000
            result["monthly_salary"] = val

        expense_match = re.search(r"(?:expense|spend|cost).*?(\d[\d,]*\.?\d*)", message, re.IGNORECASE)
        if expense_match:
            result["monthly_expenses"] = float(expense_match.group(1).replace(",", ""))

        year_match = re.search(r"(\d+)\s*(year|yr)", message, re.IGNORECASE)
        if year_match:
            result["employment_duration_years"] = int(year_match.group(1))

        if re.search(r"(?:no|don't|none|zero|not).*loan", message, re.IGNORECASE):
            result["existing_loans"] = "None"
        elif re.search(r"loan", message, re.IGNORECASE):
            result["existing_loans"] = message.strip()

        return result

    def _auto_extract_business(self, message: str) -> dict:
        import re
        result = {}
        rev_match = re.search(r"(\d[\d,]*\.?\d*)\s*(k|thousand|million)?\s*(per month|monthly|/month|revenue)", message, re.IGNORECASE)
        if rev_match:
            val = float(rev_match.group(1).replace(",", ""))
            multiplier = rev_match.group(2)
            if multiplier and "k" in multiplier.lower():
                val *= 1000
            elif multiplier and "million" in multiplier.lower():
                val *= 1000000
            result["monthly_revenue"] = val

        profit_match = re.search(r"profit.*?(\d[\d,]*\.?\d*)", message, re.IGNORECASE)
        if profit_match:
            result["monthly_profit"] = float(profit_match.group(1).replace(",", ""))

        year_match = re.search(r"(\d+)\s*(year|yr)", message, re.IGNORECASE)
        if year_match:
            result["business_years"] = int(year_match.group(1))

        name_match = re.search(r"(?:name|called|trading as).*?(?:is|:)?\s*(.+?)(?:\.|,|$)", message, re.IGNORECASE)
        if name_match and len(name_match.group(1).strip()) > 2:
            result["business_name"] = name_match.group(1).strip()

        return result

    def _auto_extract_loan(self, message: str) -> dict:
        import re
        result = {}
        amount_match = re.search(r"(\d[\d,]*\.?\d*)\s*(k|thousand|million|m|billion)?", message, re.IGNORECASE)
        if amount_match:
            val = float(amount_match.group(1).replace(",", ""))
            multiplier = amount_match.group(2)
            if multiplier:
                ml = multiplier.lower()
                if ml in ("k", "thousand"):
                    val *= 1000
                elif ml in ("m", "million"):
                    val *= 1000000
                elif ml in ("b", "billion"):
                    val *= 1000000000
            result["loan_amount"] = val

        purpose_keywords = ["for my", "for the", "purpose", "need it for", "to ", "for "]
        for kw in purpose_keywords:
            if kw in message.lower():
                idx = message.lower().index(kw) + len(kw)
                purpose_text = message[idx:].strip()
                if purpose_text:
                    result["loan_purpose"] = purpose_text.split(".")[0].strip()[:200]
                    break

        if not result.get("loan_purpose"):
            result["loan_purpose"] = message.strip()[:200]

        duration_match = re.search(r"(\d+)\s*(month|year|yr)", message, re.IGNORECASE)
        if duration_match:
            val = int(duration_match.group(1))
            unit = duration_match.group(2).lower()
            if unit in ("year", "yr"):
                val *= 12
            result["repayment_duration_months"] = val

        return result

    def _update_application(
        self, db, application: LoanApplication, extracted: dict,
        next_step: str, reply: str, user_message: str
    ) -> LoanApplication:
        for key, value in extracted.items():
            if value is not None and hasattr(application, key):
                setattr(application, key, value)

        history = application.conversation_history or []
        history.append({
            "user_message": user_message,
            "assistant_reply": reply,
            "step": application.current_step,
            "extracted": extracted,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        application.conversation_history = history
        application.current_step = next_step

        if application.full_name:
            application.status = "personal_info_collected"
        if application.employment_type:
            application.status = "profession_info_collected"
        if application.loan_amount:
            application.status = "loan_requirement_collected"

        db.commit()
        db.refresh(application)
        return application

    def _get_latest_data(self, application: LoanApplication) -> dict:
        return {
            "full_name": application.full_name,
            "cnic": application.cnic,
            "phone": application.phone,
            "email": application.email,
            "employment_type": application.employment_type,
            "company_name": application.company_name,
            "job_position": application.job_position,
            "employment_duration_years": application.employment_duration_years,
            "monthly_salary": application.monthly_salary,
            "monthly_expenses": application.monthly_expenses,
            "existing_loans": application.existing_loans,
            "business_type": application.business_type,
            "business_name": application.business_name,
            "business_years": application.business_years,
            "monthly_revenue": application.monthly_revenue,
            "monthly_profit": application.monthly_profit,
            "business_expenses": application.business_expenses,
            "existing_business_loans": application.existing_business_loans,
            "loan_amount": application.loan_amount,
            "loan_purpose": application.loan_purpose,
            "repayment_duration_months": application.repayment_duration_months,
        }

    def accept_terms(self, application_id: str) -> dict:
        db = SessionLocal()
        try:
            application = db.query(LoanApplication).filter(LoanApplication.id == application_id).first()
            if not application:
                return {"success": False, "message": "Application not found"}

            application.terms_accepted = True
            application.terms_accepted_at = datetime.now(timezone.utc)
            application.status = "terms_accepted"
            application.current_step = "agreement_generated"

            agreement = self._generate_agreement(db, application)

            db.commit()

            return {
                "success": True,
                "message": "Terms accepted! Your loan agreement has been generated.",
                "agreement": {
                    "id": agreement.id,
                    "loan_application_id": agreement.loan_application_id,
                    "agreement_text": agreement.agreement_text,
                    "payment_schedule": agreement.payment_schedule,
                    "created_at": agreement.created_at.isoformat() if agreement.created_at else "",
                },
            }
        finally:
            db.close()

    def _generate_agreement(self, db, application: LoanApplication) -> LoanAgreement:
        existing = db.query(LoanAgreement).filter(
            LoanAgreement.loan_application_id == application.id
        ).first()
        if existing:
            return existing

        duration = application.repayment_duration_months or 12
        loan_amount = application.loan_amount or 0
        monthly_payment = application.monthly_payment or (loan_amount / duration if duration else 0)
        rate = application.interest_rate or 0

        schedule = []
        balance = loan_amount
        for i in range(1, duration + 1):
            interest = balance * (rate / 100) / 12
            principal = monthly_payment - interest
            if principal < 0:
                principal = 0
            balance -= principal
            if balance < 0:
                balance = 0
            from datetime import timedelta
            due = datetime.now(timezone.utc) + timedelta(days=30 * i)
            schedule.append({
                "installment": i,
                "due_date": due.strftime("%Y-%m-%d"),
                "amount": round(monthly_payment, 2),
                "principal": round(principal, 2),
                "interest": round(interest, 2),
                "balance": round(balance, 2),
                "status": "pending",
            })

        agreement_text = (
            f"SMARTBANK LOAN AGREEMENT\n"
            f"=======================\n\n"
            f"Agreement ID: {application.id}\n"
            f"Date: {datetime.now(timezone.utc).strftime('%Y-%m-%d')}\n\n"
            f"Borrower: {application.full_name}\n"
            f"CNIC: {application.cnic}\n"
            f"Phone: {application.phone}\n"
            f"Email: {application.email}\n\n"
            f"Loan Details:\n"
            f"  Amount: ${loan_amount:,.2f}\n"
            f"  Purpose: {application.loan_purpose or 'N/A'}\n"
            f"  Duration: {duration} months\n"
            f"  Interest Rate: {rate}% per year\n"
            f"  Monthly Payment: ${monthly_payment:,.2f}\n"
            f"  Total Payment: ${application.total_payment or (monthly_payment * duration):,.2f}\n\n"
            f"Late Payment Charge: {application.late_payment_charge_rate or 2}% of missed payment amount\n\n"
            f"Terms & Conditions:\n"
            f"1. The borrower agrees to repay the loan in {duration} monthly installments.\n"
            f"2. Each installment of ${monthly_payment:,.2f} is due on the specified date.\n"
            f"3. Late payments will incur a {application.late_payment_charge_rate or 2}% charge.\n"
            f"4. Default may result in legal action and credit score impact.\n"
            f"5. Early repayment is allowed without penalty.\n\n"
            f"Payment Schedule:\n"
        )
        for inst in schedule:
            agreement_text += (
                f"  Month {inst['installment']}: Due {inst['due_date']} - "
                f"${inst['amount']:,.2f} (Principal: ${inst['principal']:,.2f}, "
                f"Interest: ${inst['interest']:,.2f})\n"
            )

        agreement_text += (
            f"\n\nBy accepting this agreement, you confirm that all information provided is accurate "
            f"and you agree to the terms and conditions stated above.\n\n"
            f"SMARTBANK - Smart Banking Solutions"
        )

        agreement = LoanAgreement(
            loan_application_id=application.id,
            agreement_text=agreement_text,
            payment_schedule=schedule,
        )
        db.add(agreement)
        db.flush()
        application.status = "agreement_generated"
        return agreement
