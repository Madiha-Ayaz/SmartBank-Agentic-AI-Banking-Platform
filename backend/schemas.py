from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime


class UserResponse(BaseModel):
    id: str
    username: str
    email: str = ""
    role: str


class CaseResponse(BaseModel):
    id: str
    customer_name: str
    type: str
    status: str
    priority: str
    channel: str
    time: str
    date: str


class CaseListResponse(BaseModel):
    cases: list[CaseResponse]
    total: int
    page: int = 1
    page_size: int = 20


class StatsResponse(BaseModel):
    total_cases: int
    resolved: int
    pending: int
    human_review: int
    critical: int
    avg_resolution_time: str
    automation_rate: int
    sla_compliance: int


class AnalyticsResponse(BaseModel):
    by_status: dict[str, int]
    by_priority: dict[str, int]
    by_channel: dict[str, int]


class ClassifyRequest(BaseModel):
    text: str
    channel: str = "web"
    language_hint: Optional[str] = None


class ClassifyResponse(BaseModel):
    request_id: str
    timestamp: str
    channel: str
    detected_language: str
    intent: dict
    entities: dict
    escalate_to_human: bool


class ChatRequest(BaseModel):
    message: str
    language: Optional[str] = None


class ChatResponse(BaseModel):
    text: str
    language: str
    module: Optional[str] = None
    escalation: bool = False
    escalation_reason: Optional[str] = None


class DocumentVerifyResponse(BaseModel):
    filename: Optional[str] = None
    size: int = 0
    document_type: str
    risk_score: float
    risk_level: str
    decision: str
    extracted_fields: dict = {}
    fraud_indicators: list = []
    processing_id: str


class AuditEntryRequest(BaseModel):
    action: str
    actor: Optional[str] = None
    resource: Optional[str] = None
    details: Optional[str] = None


class AuditEntryResponse(BaseModel):
    logged: bool
    entry_id: int


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    database: str = "connected"


class WorkflowItem(BaseModel):
    name: str
    file: str
    size: int


class WorkflowListResponse(BaseModel):
    workflows: list[WorkflowItem]


class LoanChatRequest(BaseModel):
    message: str
    application_id: Optional[str] = None
    language: Optional[str] = "en"


class LoanChatResponse(BaseModel):
    text: str
    application_id: str
    current_step: str
    data_collected: dict
    completed: bool = False


class LoanApplicationResponse(BaseModel):
    id: str
    status: str
    current_step: str
    full_name: Optional[str] = None
    cnic: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    employment_type: Optional[str] = None
    loan_amount: Optional[float] = None
    loan_purpose: Optional[str] = None
    repayment_duration_months: Optional[int] = None
    risk_level: Optional[str] = None
    credit_score: Optional[int] = None
    interest_rate: Optional[float] = None
    monthly_payment: Optional[float] = None
    decision_reason: Optional[str] = None
    terms_accepted: bool = False
    created_at: str
    updated_at: str


class LoanAgreementResponse(BaseModel):
    id: str
    loan_application_id: str
    agreement_text: str
    payment_schedule: list
    created_at: str


class LoanAcceptTermsRequest(BaseModel):
    application_id: str
    accepted: bool


class LoanAcceptTermsResponse(BaseModel):
    success: bool
    message: str
    agreement: Optional[LoanAgreementResponse] = None


class TransactionProcessRequest(BaseModel):
    transaction_id: str = Field(..., description="Transaction reference ID")
    customer_name: str = Field(..., description="Customer name")
    amount: float = Field(gt=0, description="Transaction amount")
    bank_routing_number: Optional[str] = Field(None, description="Account number or bank routing number for admin-to-customer transfer")
    account_number: Optional[str] = Field(None, alias="accountNumber", description="Alias for bank_routing_number")
    description: Optional[str] = Field(None, description="Transaction description")
    sender_account: Optional[str] = Field(None, description="Sender account (defaults to system admin account)")


class TransactionProcessResponse(BaseModel):
    success: bool
    workflow_id: str
    transaction_type: str
    transaction_id: Optional[str] = None
    sender_name: Optional[str] = None
    receiver_name: Optional[str] = None
    receiver_account: Optional[str] = None
    amount: float = 0
    routing_verified: bool = False
    message: str
    timestamp: str
