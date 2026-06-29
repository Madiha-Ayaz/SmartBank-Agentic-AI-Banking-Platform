import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, JSON, Text, Enum as SAEnum
from backend.database import Base
import enum


class CasePriority(enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class CaseStatus(enum.Enum):
    PENDING = "Pending"
    IN_PROGRESS = "In Progress"
    OTP_SENT = "OTP Sent"
    HUMAN_REVIEW = "Human Review"
    RESOLVED = "Resolved"
    CLOSED = "Closed"
    ESCALATED = "Escalated"
    QUEUED = "Queued"
    REJECTED = "Rejected"


# ─── State Machine: Valid transitions for Case lifecycle ───
CASE_STATE_MACHINE: dict[str, list[str]] = {
    "Pending":        ["In Progress", "Human Review", "Resolved", "Closed", "Escalated", "Rejected"],
    "In Progress":    ["OTP Sent", "Human Review", "Resolved", "Escalated", "Rejected"],
    "OTP Sent":       ["In Progress", "Resolved", "Human Review"],
    "Human Review":   ["In Progress", "Resolved", "Rejected", "Escalated"],
    "Resolved":       ["Closed"],
    "Closed":         [],
    "Escalated":      ["In Progress", "Human Review", "Resolved"],
    "Queued":         ["Pending", "In Progress"],
    "Rejected":       ["Closed"],
}


def validate_case_transition(current_status: str, new_status: str) -> bool:
    """Validate if a case status transition is allowed per the state machine.
    
    Args:
        current_status: Current status of the case
        new_status: Proposed new status
        
    Returns:
        True if the transition is valid, False otherwise
    """
    allowed = CASE_STATE_MACHINE.get(current_status, [])
    if new_status in allowed:
        return True
    return False


class IntentCode(enum.Enum):
    ATM01 = "ATM Card Activation"
    PIN02 = "PIN Generation/Reset"
    DEB03 = "Debit Card Block/Unblock"
    STM04 = "Bank Statement Generation"
    LTR05 = "Account Opening Letter"
    NIC06 = "Identity Card/CNIC Update"
    IB07 = "Internet Banking Access Recovery"
    MB08 = "Mobile Banking Activation"


def gen_id():
    return str(uuid.uuid4())[:8].upper()


def now_utc():
    return datetime.now(timezone.utc)


class Customer(Base):
    __tablename__ = "customers"
    id = Column(String, primary_key=True, default=gen_id)
    name = Column(String, nullable=False)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    cnic = Column(String, nullable=True)
    account_number = Column(String, nullable=True)
    created_at = Column(DateTime, default=now_utc)


class Case(Base):
    __tablename__ = "cases"
    id = Column(String, primary_key=True, default=gen_id)
    customer_id = Column(String, nullable=False)
    customer_name = Column(String, nullable=False)
    type = Column(String, nullable=False)
    status = Column(String, default="Pending")
    priority = Column(String, default="Medium")
    channel = Column(String, default="Web")
    time = Column(String, default="—")
    date = Column(String, default="")
    intent_code = Column(String, nullable=True)
    created_at = Column(DateTime, default=now_utc)
    updated_at = Column(DateTime, default=now_utc, onupdate=now_utc)


class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, default=gen_id)
    firebase_uid = Column(String, unique=True, nullable=False)
    username = Column(String, nullable=False)
    email = Column(String, nullable=True)
    role = Column(String, default="agent")
    created_at = Column(DateTime, default=now_utc)


class AuthLog(Base):
    __tablename__ = "auth_logs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=now_utc)
    action = Column(String, nullable=False)
    email = Column(String, nullable=True)
    uid = Column(String, nullable=True)
    name = Column(String, nullable=True)
    ip_address = Column(String, nullable=True)


class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=now_utc)
    action = Column(String, nullable=False)
    actor = Column(String, nullable=True)
    resource = Column(String, nullable=True)
    details = Column(Text, nullable=True)
    previous_hash = Column(String, nullable=True)
    hash = Column(String, nullable=True)


class DocumentVerification(Base):
    __tablename__ = "document_verifications"
    id = Column(String, primary_key=True, default=gen_id)
    customer_id = Column(String, nullable=True)
    filename = Column(String, nullable=True)
    document_type = Column(String, nullable=True)
    risk_score = Column(Float, default=0.0)
    risk_level = Column(String, default="low")
    decision = Column(String, nullable=True)
    fraud_indicators = Column(JSON, default=list)
    extracted_fields = Column(JSON, default=dict)
    created_at = Column(DateTime, default=now_utc)


class LoanApplication(Base):
    __tablename__ = "loan_applications"
    id = Column(String, primary_key=True, default=gen_id)
    customer_id = Column(String, nullable=True)

    full_name = Column(String, nullable=True)
    cnic = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    email = Column(String, nullable=True)

    employment_type = Column(String, nullable=True)
    company_name = Column(String, nullable=True)
    job_position = Column(String, nullable=True)
    employment_duration_years = Column(Integer, nullable=True)
    monthly_salary = Column(Float, nullable=True)
    monthly_expenses = Column(Float, nullable=True)
    existing_loans = Column(Text, nullable=True)

    business_type = Column(String, nullable=True)
    business_name = Column(String, nullable=True)
    business_years = Column(Integer, nullable=True)
    monthly_revenue = Column(Float, nullable=True)
    monthly_profit = Column(Float, nullable=True)
    business_expenses = Column(Float, nullable=True)
    existing_business_loans = Column(Text, nullable=True)

    loan_amount = Column(Float, nullable=True)
    loan_purpose = Column(String, nullable=True)
    repayment_duration_months = Column(Integer, nullable=True)

    income_stability_score = Column(Float, nullable=True)
    debt_ratio = Column(Float, nullable=True)
    repayment_capability_score = Column(Float, nullable=True)
    credit_score = Column(Integer, nullable=True)
    risk_level = Column(String, nullable=True)
    risk_factors = Column(JSON, nullable=True)

    status = Column(String, default="draft")
    decision_reason = Column(Text, nullable=True)
    improvement_suggestions = Column(JSON, nullable=True)

    interest_rate = Column(Float, nullable=True)
    monthly_payment = Column(Float, nullable=True)
    total_payment = Column(Float, nullable=True)
    late_payment_charge_rate = Column(Float, nullable=True)
    terms_accepted = Column(Boolean, default=False)
    terms_accepted_at = Column(DateTime, nullable=True)

    conversation_history = Column(JSON, default=list)
    current_step = Column(String, default="greeting")
    created_at = Column(DateTime, default=now_utc)
    updated_at = Column(DateTime, default=now_utc, onupdate=now_utc)


class LoanAgreement(Base):
    __tablename__ = "loan_agreements"
    id = Column(String, primary_key=True, default=gen_id)
    loan_application_id = Column(String, nullable=False)
    agreement_text = Column(Text, nullable=True)
    payment_schedule = Column(JSON, default=list)
    signed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=now_utc)


class FinanceCustomer(Base):
    __tablename__ = "finance_customers"
    customer_id = Column(Integer, primary_key=True, autoincrement=False)
    full_name = Column(String(200), nullable=False)
    father_name = Column(String(200), nullable=True)
    mother_name = Column(String(200), nullable=True)
    date_of_birth = Column(String(20), nullable=True)
    cnic_dummy = Column(String(20), unique=True, nullable=True)
    phone = Column(String(20), nullable=True)
    email = Column(String(200), nullable=True)
    address = Column(Text, nullable=True)
    city = Column(String(100), nullable=True)
    profession = Column(String(200), nullable=True)
    employment_type = Column(String(50), nullable=True)
    monthly_income = Column(Float, default=0.0)
    account_number = Column(String(50), unique=True, nullable=False)
    account_balance = Column(Float, default=0.0)
    credit_score = Column(Integer, default=0)
    existing_loan = Column(Boolean, default=False)
    loan_limits = Column(Float, default=0.0)
    bank_routing_number = Column(String(20), nullable=True)
    password = Column(String(200), nullable=True)
    created_at = Column(DateTime, default=now_utc)


class FinanceTransaction(Base):
    __tablename__ = "finance_transactions"
    id = Column(String, primary_key=True, default=gen_id)
    sender_account = Column(String(50), nullable=False)
    receiver_account = Column(String(50), nullable=False)
    sender_name = Column(String(200), nullable=True)
    receiver_name = Column(String(200), nullable=True)
    amount = Column(Float, nullable=False)
    type = Column(String(20), default="transfer")
    status = Column(String(20), default="completed")
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=now_utc)
