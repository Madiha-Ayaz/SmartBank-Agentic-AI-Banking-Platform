from __future__ import annotations

import io
import logging
import tempfile
from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile

from backend.cache import cache
from backend.database import SessionLocal
from backend.models import DocumentVerification
from backend.schemas import DocumentVerifyResponse
from document_ai.pipeline import DocumentAIPipeline

logger = logging.getLogger("smartbank.routers.document")
router = APIRouter(prefix="/api", tags=["Document AI"])

doc_pipeline = DocumentAIPipeline()


@router.post("/document/verify", response_model=DocumentVerifyResponse)
async def verify_document(file: UploadFile) -> DocumentVerifyResponse:
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename required")

    contents = await file.read()
    size = len(contents)

    try:
        suffix = Path(file.filename).suffix or ".png"
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            tmp.write(contents)
            tmp_path = tmp.name

        result = doc_pipeline.process_document(tmp_path, "demo-customer")

        db = SessionLocal()
        try:
            doc = DocumentVerification(
                filename=file.filename,
                document_type=result.ocr.fields[0].name if result.ocr and result.ocr.fields else "Unknown",
                risk_score=result.fraud.risk_score if result.fraud else 0.0,
                risk_level=result.fraud.risk_level.value if result.fraud else "safe",
                decision=result.overall_status,
                fraud_indicators=[i["indicator"] for i in (result.fraud.indicators_triggered if result.fraud else [])],
                extracted_fields=(
                    {f.name: f.value for f in result.ocr.fields}
                    if result.ocr and result.ocr.fields
                    else {"status": "simulated"}
                ),
            )
            db.add(doc)
            db.commit()

            await cache.invalidate_pattern("documents:*")

            return DocumentVerifyResponse(
                filename=file.filename,
                size=size,
                document_type=doc.document_type,
                risk_score=doc.risk_score,
                risk_level=doc.risk_level,
                decision=doc.decision,
                extracted_fields=doc.extracted_fields,
                fraud_indicators=doc.fraud_indicators,
                processing_id=doc.id,
            )
        finally:
            db.close()
            Path(tmp_path).unlink(missing_ok=True)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Document processing failed: {e}")
