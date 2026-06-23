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
    clerk_id = Column(String, unique=True, nullable=False)
    username = Column(String, nullable=False)
    email = Column(String, nullable=True)
    role = Column(String, default="agent")
    created_at = Column(DateTime, default=now_utc)


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
