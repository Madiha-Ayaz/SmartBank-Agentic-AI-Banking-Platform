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
