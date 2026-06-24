from __future__ import annotations

import datetime
from sqlalchemy import Column, String, Float, Integer, DateTime, Boolean, Text, Enum as SAEnum, ForeignKey
from sqlalchemy.orm import relationship
import enum

from banking_api.database import Base


class KYCStatus(str, enum.Enum):
    VERIFIED = "verified"
    PENDING = "pending"
    REJECTED = "rejected"


class RiskLevel(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class AccountStatus(str, enum.Enum):
    ACTIVE = "active"
    FROZEN = "frozen"
    CLOSED = "closed"
    BLOCKED = "blocked"


class TransactionStatus(str, enum.Enum):
    COMPLETED = "completed"
    PENDING = "pending"
    FAILED = "failed"
    REFUNDED = "refunded"
    DISPUTED = "disputed"


class TransactionType(str, enum.Enum):
    DEBIT = "debit"
    CREDIT = "credit"
    REFUND = "refund"
    PAYMENT = "payment"
    TRANSFER = "transfer"


class FraudStatus(str, enum.Enum):
    OPEN = "open"
    UNDER_REVIEW = "under_review"
    CONFIRMED = "confirmed"
    FALSE_POSITIVE = "false_positive"
    RESOLVED = "resolved"


class CardStatus(str, enum.Enum):
    ACTIVE = "active"
    BLOCKED = "blocked"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class CardType(str, enum.Enum):
    DEBIT = "debit"
    CREDIT = "credit"


class Customer(Base):
    __tablename__ = "customers"

    customer_id = Column(String(20), primary_key=True)
    name = Column(String(200), nullable=False)
    email = Column(String(200), nullable=False)
    phone = Column(String(20), nullable=False)
    account_type = Column(String(50), default="Standard")
    monthly_income = Column(Float, default=0.0)
    monthly_expense = Column(Float, default=0.0)
    kyc_status = Column(SAEnum(KYCStatus), default=KYCStatus.VERIFIED)
    risk_level = Column(SAEnum(RiskLevel), default=RiskLevel.LOW)
    saving_score = Column(Integer, default=50)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    accounts = relationship("Account", back_populates="customer", lazy="selectin")
    transactions = relationship("Transaction", back_populates="customer", lazy="selectin")
    cards = relationship("Card", back_populates="customer", lazy="selectin")

    def to_dict(self):
        return {
            "customer_id": self.customer_id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "account_type": self.account_type,
            "kyc_status": self.kyc_status.value if self.kyc_status else "verified",
            "risk_level": self.risk_level.value if self.risk_level else "low",
            "monthly_income": self.monthly_income,
            "monthly_expense": self.monthly_expense,
            "saving_score": self.saving_score,
        }


class Account(Base):
    __tablename__ = "accounts"

    account_id = Column(String(20), primary_key=True)
    customer_id = Column(String(20), ForeignKey("customers.customer_id"), nullable=False)
    balance = Column(Float, default=0.0)
    currency = Column(String(3), default="PKR")
    account_status = Column(SAEnum(AccountStatus), default=AccountStatus.ACTIVE)
    account_type = Column(String(50), default="Current")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    customer = relationship("Customer", back_populates="accounts")

    def to_dict(self):
        return {
            "account_id": self.account_id,
            "customer_id": self.customer_id,
            "balance": self.balance,
            "currency": self.currency,
            "account_status": self.account_status.value if self.account_status else "active",
            "account_type": self.account_type,
        }


class Transaction(Base):
    __tablename__ = "transactions"

    transaction_id = Column(String(20), primary_key=True)
    customer_id = Column(String(20), ForeignKey("customers.customer_id"), nullable=False)
    account_id = Column(String(20), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String(3), default="PKR")
    merchant = Column(String(200), nullable=False)
    merchant_ref = Column(String(100), default="")
    location = Column(String(100), default="")
    category = Column(String(50), default="General")
    transaction_type = Column(SAEnum(TransactionType), default=TransactionType.DEBIT)
    status = Column(SAEnum(TransactionStatus), default=TransactionStatus.COMPLETED)
    failure_reason = Column(String(500), default="")
    is_international = Column(Boolean, default=False)
    is_online = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    customer = relationship("Customer", back_populates="transactions")

    def to_dict(self):
        return {
            "transaction_id": self.transaction_id,
            "customer_id": self.customer_id,
            "account_id": self.account_id,
            "amount": self.amount,
            "currency": self.currency,
            "merchant": self.merchant,
            "merchant_ref": self.merchant_ref,
            "location": self.location,
            "category": self.category,
            "transaction_type": self.transaction_type.value if self.transaction_type else "debit",
            "status": self.status.value if self.status else "completed",
            "failure_reason": self.failure_reason,
            "is_international": self.is_international,
            "is_online": self.is_online,
            "date": self.created_at.isoformat() if self.created_at else "",
        }


class FraudCase(Base):
    __tablename__ = "fraud_cases"

    case_id = Column(String(20), primary_key=True)
    transaction_id = Column(String(20), nullable=False)
    customer_id = Column(String(20), nullable=False)
    risk_score = Column(Float, default=0.0)
    risk_level = Column(String(20), default="low")
    indicators = Column(Text, default="[]")
    status = Column(SAEnum(FraudStatus), default=FraudStatus.OPEN)
    recommended_action = Column(String(200), default="")
    reviewed_by = Column(String(100), default="")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)

    def to_dict(self):
        import json
        return {
            "case_id": self.case_id,
            "transaction_id": self.transaction_id,
            "customer_id": self.customer_id,
            "risk_score": self.risk_score,
            "risk_level": self.risk_level,
            "indicators": json.loads(self.indicators) if self.indicators else [],
            "status": self.status.value if self.status else "open",
            "recommended_action": self.recommended_action,
            "reviewed_by": self.reviewed_by,
            "created_at": self.created_at.isoformat() if self.created_at else "",
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else "",
        }


class Card(Base):
    __tablename__ = "cards"

    card_id = Column(String(20), primary_key=True)
    customer_id = Column(String(20), ForeignKey("customers.customer_id"), nullable=False)
    card_number = Column(String(20), nullable=False)
    card_type = Column(SAEnum(CardType), default=CardType.DEBIT)
    status = Column(SAEnum(CardStatus), default=CardStatus.ACTIVE)
    expiry_date = Column(String(10), default="")
    block_reason = Column(String(500), default="")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    customer = relationship("Customer", back_populates="cards")

    def to_dict(self):
        return {
            "card_id": self.card_id,
            "customer_id": self.customer_id,
            "card_number": f"****{self.card_number[-4:]}" if self.card_number else "****",
            "card_type": self.card_type.value if self.card_type else "debit",
            "status": self.status.value if self.status else "active",
            "expiry_date": self.expiry_date,
            "block_reason": self.block_reason,
        }


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, autoincrement=True)
    notification_id = Column(String(20), unique=True, nullable=False)
    customer_id = Column(String(20), nullable=False)
    channel = Column(String(20), nullable=False)
    message = Column(Text, nullable=False)
    status = Column(String(20), default="sent")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    def to_dict(self):
        return {
            "notification_id": self.notification_id,
            "customer_id": self.customer_id,
            "channel": self.channel,
            "message": self.message,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else "",
        }
