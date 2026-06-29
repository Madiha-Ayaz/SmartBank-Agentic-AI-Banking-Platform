from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException

from agents.classification_agent.classifier import SmartBankIntentClassifier
from backend.schemas import ClassifyRequest, ClassifyResponse

logger = logging.getLogger("smartbank.routers.classify")
router = APIRouter(prefix="/api", tags=["Classification"])

classifier = SmartBankIntentClassifier(config={"confidence_threshold": 0.65})


@router.post("/classify", response_model=ClassifyResponse)
async def classify_request(body: ClassifyRequest) -> ClassifyResponse:
    if not body.text:
        raise HTTPException(status_code=400, detail="text is required")
    try:
        result = classifier.classify(body.text, body.channel, body.language_hint)
        return ClassifyResponse(
            request_id=result.request_id,
            timestamp=result.timestamp,
            channel=result.channel,
            detected_language=result.detected_language,
            intent={
                "code": result.intent.code,
                "label": result.intent.label,
                "confidence": result.intent.confidence,
            },
            entities=result.entities,
            escalate_to_human=result.escalate_to_human,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
