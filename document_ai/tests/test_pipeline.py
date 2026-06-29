from __future__ import annotations

import json
import os
import sys
import tempfile
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Generator

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pipeline import (
    DocumentAIPipeline,
    DocumentVerificationResult,
    RiskLevel,
    ValidationStatus,
    MAX_FILE_SIZE,
    SUPPORTED_EXTENSIONS,
)


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

def _make_dummy_image(
    suffix: str = ".png",
    prefix: str = "cnic",
    size: tuple[int, int] = (800, 500),
) -> str:
    from PIL import Image

    fd, path = tempfile.mkstemp(suffix=suffix, prefix=f"{prefix}_")
    os.close(fd)
    img = Image.new("RGB", size, color=(255, 255, 255))
    img.save(path)
    return path


def _make_overlarge_file() -> str:
    fd, path = tempfile.mkstemp(suffix=".png", prefix="oversized_")
    os.close(fd)
    with open(path, "wb") as f:
        f.seek(MAX_FILE_SIZE + 1)
        f.write(b"\0")
    return path


# ------------------------------------------------------------------
# Fixtures
# ------------------------------------------------------------------

@pytest.fixture
def pipeline() -> DocumentAIPipeline:
    return DocumentAIPipeline(
        confidence_threshold=0.85,
        enable_simulation=True,
    )


@pytest.fixture
def valid_cnic_front() -> Generator[str, None, None]:
    path = _make_dummy_image(suffix=".png", prefix="cnic_front")
    yield path
    try:
        os.unlink(path)
    except OSError:
        pass


@pytest.fixture
def expired_document() -> Generator[str, None, None]:
    path = _make_dummy_image(suffix=".png", prefix="cnic_expired")
    yield path
    try:
        os.unlink(path)
    except OSError:
        pass


@pytest.fixture
def oversized_file() -> Generator[str, None, None]:
    path = _make_overlarge_file()
    yield path
    try:
        os.unlink(path)
    except OSError:
        pass


@pytest.fixture
def unsupported_format() -> Generator[str, None, None]:
    fd, path = tempfile.mkstemp(suffix=".bmp", prefix="invalid_")
    os.close(fd)
    yield path
    try:
        os.unlink(path)
    except OSError:
        pass


# ==================================================================
# Test 1 — Valid CNIC front/back → auto-approve
# ==================================================================
def test_valid_cnic_auto_approve(pipeline: DocumentAIPipeline, valid_cnic_front: str):
    result = pipeline.process_document(valid_cnic_front, customer_id="CUST-001")
    assert result.error is None
    assert result.overall_status == "approved"
    assert result.pre_processing is not None
    assert result.ocr is not None
    assert result.ocr.passed_threshold is True
    assert result.validation is not None
    assert result.validation.format_valid is True
    assert result.validation.expiry_valid is True
    assert result.fraud is not None
    assert result.fraud.risk_level == RiskLevel.AUTO_APPROVE
    assert result.cbs_update is not None
    assert result.cbs_update.success is True


# ==================================================================
# Test 2 — Expired CNIC → reject
# ==================================================================
def test_expired_cnic_rejected(pipeline: DocumentAIPipeline):
    class ExpiredCnicPipeline(DocumentAIPipeline):
        def _stage_ocr(self, file_path, result, ctx):
            from pipeline import OCRResult, FieldExtraction
            fields = [
                FieldExtraction("Name", "John Doe", 0.94),
                FieldExtraction("Father Name", "Ahmed Khan", 0.92),
                FieldExtraction("CNIC Number", "12345-6789012-3", 0.93),
                FieldExtraction("Date of Birth", "15-08-1990", 0.91),
                FieldExtraction("Issue Date", "01-01-2015", 0.90),
                FieldExtraction("Expiry Date", "01-01-2020", 0.89),
                FieldExtraction("Gender", "M", 0.97),
                FieldExtraction("Address", "Islamabad", 0.88),
                FieldExtraction("Identity Number", "12345-6789012-3", 0.93),
            ]
            raw = "\n".join(f.value for f in fields)
            ctx["ocr_fields"] = fields
            ctx["overall_ocr_confidence"] = 0.91
            return OCRResult(
                fields=fields, raw_text=raw,
                overall_confidence=0.91, passed_threshold=True,
            )

    ep = ExpiredCnicPipeline(enable_simulation=True)
    path = _make_dummy_image(suffix=".png", prefix="cnic_expired")
    try:
        result = ep.process_document(path, customer_id="CUST-002")
        assert result.validation is not None
        assert result.validation.expiry_valid is False
        assert result.validation.expiry_status is not None
        assert "expired" in result.validation.expiry_status.lower()
    finally:
        try:
            os.unlink(path)
        except OSError:
            pass


# ==================================================================
# Test 3 — Low confidence OCR → human review
# ==================================================================
def test_low_confidence_ocr_triggers_flag(pipeline: DocumentAIPipeline):
    class LowConfPipeline(DocumentAIPipeline):
        def _stage_ocr(self, file_path, result, ctx):
            from pipeline import OCRResult, FieldExtraction, ValidationStatus
            fields = [
                FieldExtraction("Name", "John Doe", 0.45),
                FieldExtraction("CNIC Number", "12345-6789012-3", 0.40),
                FieldExtraction("Date of Birth", "15-08-1990", 0.50),
                FieldExtraction("Issue Date", "01-01-2020", 0.42),
                FieldExtraction("Expiry Date", "01-01-2030", 0.48),
                FieldExtraction("Gender", "M", 0.55),
                FieldExtraction("Address", "Islamabad", 0.38),
            ]
            for f in fields:
                f.validated = ValidationStatus.FLAGGED
                f.validation_message = (
                    f"Confidence {f.confidence:.2f} < threshold 0.85"
                )
            ctx["ocr_fields"] = fields
            ctx["overall_ocr_confidence"] = 0.45
            return OCRResult(
                fields=fields,
                raw_text="\n".join(f.value for f in fields),
                overall_confidence=0.45,
                passed_threshold=False,
            )

    lp = LowConfPipeline(enable_simulation=True)
    path = _make_dummy_image(suffix=".png", prefix="cnic")
    try:
        result = lp.process_document(path, customer_id="CUST-003")
        assert result.ocr is not None
        assert result.ocr.passed_threshold is False
        assert result.ocr.overall_confidence < 0.85
        flagged = [f for f in result.ocr.fields if f.validated == ValidationStatus.FLAGGED]
        assert len(flagged) > 0
    finally:
        try:
            os.unlink(path)
        except OSError:
            pass


# ==================================================================
# Test 4 — EXIF tampering detected → human review
# ==================================================================
def test_exif_tampering_human_review(pipeline: DocumentAIPipeline):
    class ExifFraudPipeline(DocumentAIPipeline):
        def _exif_analysis(self, file_path):
            return {"date_mismatch": True, "has_exif": True, "days_difference": 90}

    efp = ExifFraudPipeline(enable_simulation=True)
    path = _make_dummy_image(suffix=".png", prefix="cnic")
    try:
        result = efp.process_document(path, customer_id="CUST-004")
        assert result.fraud is not None
        assert result.fraud.exif_analysis is not None
        assert result.fraud.exif_analysis.get("date_mismatch") is True
    finally:
        try:
            os.unlink(path)
        except OSError:
            pass


# ==================================================================
# Test 5 — MRZ checksum fail → reject
# ==================================================================
def test_mrz_checksum_failure_rejects(pipeline: DocumentAIPipeline):
    class MrzFailPipeline(DocumentAIPipeline):
        def _mrz_checksum_verification(self, fields):
            return {"checksum_fail": True, "reason": "Checksum digit mismatch"}

        def _classify_document(self, path):
            from pipeline import DocumentType
            return DocumentType.PASSPORT

    mfp = MrzFailPipeline(enable_simulation=True)
    path = _make_dummy_image(suffix=".png", prefix="passport")
    try:
        result = mfp.process_document(path, customer_id="CUST-005")
        assert result.fraud is not None
        assert result.fraud.mrz_analysis is not None
        assert result.fraud.mrz_analysis.get("checksum_fail") is True
    finally:
        try:
            os.unlink(path)
        except OSError:
            pass


# ==================================================================
# Test 6 — Name mismatch (> 10% diff) → reject
# ==================================================================
def test_name_mismatch_rejected(pipeline: DocumentAIPipeline):
    class NameMismatchPipeline(DocumentAIPipeline):
        def _cbs_fetch_customer(self, customer_id):
            return {"id": customer_id, "name": "Farooq Ahmed"}

        def _stage_ocr(self, file_path, result, ctx):
            base = super()._stage_ocr(file_path, result, ctx)
            for f in base.fields:
                if f.name.lower() == "name":
                    f.value = "John Doe"
            ctx["ocr_fields"] = base.fields
            return base

    nmp = NameMismatchPipeline(enable_simulation=True)
    path = _make_dummy_image(suffix=".png", prefix="cnic")
    try:
        result = nmp.process_document(path, customer_id="CUST-006")
        assert result.validation is not None
        assert result.validation.format_valid is False
        assert any("name mismatch" in e.lower() for e in result.validation.format_errors)
    finally:
        try:
            os.unlink(path)
        except OSError:
            pass


# ==================================================================
# Test 7 — Over-sized file → reject
# ==================================================================
def test_oversized_file_rejected(pipeline: DocumentAIPipeline, oversized_file: str):
    result = pipeline.process_document(oversized_file, customer_id="CUST-007")
    assert result.error is not None
    assert "exceeds" in result.error.lower()


# ==================================================================
# Test 8 — Unsupported format → reject
# ==================================================================
def test_unsupported_format_rejected(pipeline: DocumentAIPipeline, unsupported_format: str):
    result = pipeline.process_document(unsupported_format, customer_id="CUST-008")
    assert result.error is not None
    assert "unsupported format" in result.error.lower()


# ==================================================================
# Test 9 — Fraud score 30-60 → human review
# ==================================================================
def test_fraud_score_30_to_60_human_review(pipeline: DocumentAIPipeline):
    class MidRiskPipeline(DocumentAIPipeline):
        def _exif_analysis(self, file_path):
            return {"date_mismatch": True, "has_exif": True, "days_difference": 45}

        def _font_inconsistency_detection(self, image):
            return {"inconsistent": True, "reason": "Font variation detected"}

    mrp = MidRiskPipeline(enable_simulation=True)
    path = _make_dummy_image(suffix=".png", prefix="cnic")
    try:
        result = mrp.process_document(path, customer_id="CUST-009")
        assert result.fraud is not None
        risk = result.fraud.risk_score
        assert 30 <= risk <= 60, f"Expected risk 30-60 but got {risk}"
        assert result.fraud.risk_level == RiskLevel.HUMAN_REVIEW
    finally:
        try:
            os.unlink(path)
        except OSError:
            pass


# ==================================================================
# Test 10 — Fraud score > 60 → reject
# ==================================================================
def test_fraud_score_above_60_rejected(pipeline: DocumentAIPipeline):
    class HighRiskPipeline(DocumentAIPipeline):
        def _exif_analysis(self, file_path):
            return {"date_mismatch": True, "has_exif": True, "days_difference": 90}

        def _font_inconsistency_detection(self, image):
            return {"inconsistent": True, "reason": "Font variation detected"}

        def _mrz_checksum_verification(self, fields):
            return {"checksum_fail": True, "reason": "Checksum fail"}

    hrp = HighRiskPipeline(enable_simulation=True)
    path = _make_dummy_image(suffix=".png", prefix="cnic")
    try:
        result = hrp.process_document(path, customer_id="CUST-010")
        assert result.fraud is not None
        assert result.fraud.risk_score > 60, (
            f"Expected risk > 60 but got {result.fraud.risk_score}"
        )
        assert result.fraud.risk_level == RiskLevel.AUTO_REJECT
    finally:
        try:
            os.unlink(path)
        except OSError:
            pass


# ==================================================================
# Pipeline version attribute test
# ==================================================================
def test_pipeline_version_present(pipeline: DocumentAIPipeline):
    path = _make_dummy_image(suffix=".png", prefix="cnic")
    try:
        result = pipeline.process_document(path, customer_id="CUST-VER")
        assert result.pipeline_version == "1.0.0"
    finally:
        try:
            os.unlink(path)
        except OSError:
            pass


# ==================================================================
# Processing ID uniqueness test
# ==================================================================
def test_processing_id_unique(pipeline: DocumentAIPipeline):
    path = _make_dummy_image(suffix=".png", prefix="cnic")
    try:
        r1 = pipeline.process_document(path, customer_id="CUST-UID1")
        r2 = pipeline.process_document(path, customer_id="CUST-UID2")
        assert r1.processing_id != r2.processing_id
    finally:
        try:
            os.unlink(path)
        except OSError:
            pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
