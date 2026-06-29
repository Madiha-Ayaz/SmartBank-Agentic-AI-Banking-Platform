from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException

from agents.customer_assistant.assistant import SmartBankAssistant
from backend.schemas import ChatRequest, ChatResponse

logger = logging.getLogger("smartbank.routers.chat")
router = APIRouter(prefix="/api", tags=["Chat"])

assistant = SmartBankAssistant()


@router.post("/chat", response_model=ChatResponse)
async def chat(body: ChatRequest) -> ChatResponse:
    if not body.message:
        raise HTTPException(status_code=400, detail="message is required")
    try:
        result = assistant.process_message(body.message, body.language or "en")
        return ChatResponse(
            text=result.text,
            language=result.language.value if result.language else "en",
            module=result.module,
            escalation=result.escalation,
            escalation_reason=result.escalation_reason,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/assistant/info")
def assistant_info() -> dict:
    return {
        "name": "Zara",
        "modules": [
            "Product Education",
            "Process Guidance",
            "SME Literacy",
            "Digital Onboarding",
            "Safety & Fraud",
        ],
    }
