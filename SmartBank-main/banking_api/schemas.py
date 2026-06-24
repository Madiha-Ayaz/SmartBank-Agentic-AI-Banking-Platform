from __future__ import annotations

import datetime
from typing import Any, Optional
from pydantic import BaseModel, Field


# --- Customer ---

class CustomerResponse(BaseModel):
    customer_id: str
    name: str
    email: str
    phone: str
    account_type: str
    kyc_status: str
    risk_level: str
    monthly_income: Optional[float] = 0
    monthly_expense: Optional[float] = 0
    saving_score: Optional[int] = 50


# --- Account ---

class AccountBalanceResponse(BaseModel):
    account_id: str
    customer_id: str
    balance: float
    currency: str
    account_status: str
    account_type: Optional[str] = "Current"


# --- Transaction ---

class TransactionResponse(BaseModel):
    transaction_id: str
    customer_id: str
    account_id: str
    amount: float
    currency: str
    merchant: str
    merchant_ref: Optional[str] = ""
    location: Optional[str] = ""
    category: Optional[str] = "General"
    transaction_type: str
    status: str
    failure_reason: Optional[str] = ""
    is_international: Optional[bool] = False
    is_online: Optional[bool] = False
    date: Optional[str] = ""


# --- Fraud ---

class FraudCheckRequest(BaseModel):
    customer_id: str
    transaction_id: str
    amount: float
    merchant: Optional[str] = ""
    location: Optional[str] = ""
    is_international: Optional[bool] = False


class FraudCheckResponse(BaseModel):
    risk_score: float
    risk_level: str
    recommended_action: str
    indicators: list[str] = []
    case_id: Optional[str] = ""


# --- Payment ---

class PaymentRequest(BaseModel):
    account_id: str
    amount: float
    merchant: str
    category: Optional[str] = "General"


class PaymentResponse(BaseModel):
    transaction_id: str
    payment_status: str
    message: str
    balance_after: Optional[float] = None


# --- Refund ---

class RefundRequest(BaseModel):
    transaction_id: str
    reason: Optional[str] = "payment_failed"


class RefundResponse(BaseModel):
    refund_id: str
    status: str
    estimated_days: int
    message: Optional[str] = ""


# --- Card ---

class CardBlockRequest(BaseModel):
    customer_id: str
    card_id: Optional[str] = ""
    reason: str = "fraud_detected"


class CardBlockResponse(BaseModel):
    card_status: str
    message: str


class CardUnblockRequest(BaseModel):
    customer_id: str
    card_id: str


class CardUnblockResponse(BaseModel):
    card_status: str
    message: str


# --- Notification ---

class NotificationRequest(BaseModel):
    customer_id: str
    channel: str = Field(..., description="SMS, EMAIL, WHATSAPP, PUSH")
    message: str
    template: Optional[str] = ""


class NotificationResponse(BaseModel):
    notification_id: str
    status: str
    channel: str


# --- Financial Health ---

class FinancialHealthResponse(BaseModel):
    customer_id: str
    monthly_income: float
    monthly_expense: float
    saving_score: float
    saving_potential: float = 0
    recommendation: str
    spending_breakdown: list[dict[str, Any]] = []


# --- Generic ---

class ErrorResponse(BaseModel):
    detail: str
    code: Optional[str] = None
