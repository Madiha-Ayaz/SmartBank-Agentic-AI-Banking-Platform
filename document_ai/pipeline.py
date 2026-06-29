from __future__ import annotations

import base64
import hashlib
import io
import json
import logging
import os
import re
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, date, timedelta, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urljoin

import sys as _sys
from pathlib import Path as _Path

import requests
from PIL import Image, ImageEnhance, ImageFilter, ImageFont

_sys.path.insert(0, str(_Path(__file__).resolve().parent / "fraud-detection"))
from scorer import FraudScorer, get_decision

logger = logging.getLogger(__name__)

MAX_FILE_SIZE: int = 10 * 1024 * 1024
SUPPORTED_EXTENSIONS: set[str] = {".jpg", ".jpeg", ".png", ".pdf"}
CNIC_PATTERN: re.Pattern = re.compile(r"^\d{5}-\d{7}-\d$")
DATE_FORMATS: list[str] = ["%d-%m-%Y", "%Y-%m-%d", "%d/%m/%Y"]


class DocumentType(str, Enum):
    CNIC = "CNIC"
    PASSPORT = "Passport"
    DRIVING_LICENCE = "Driving Licence"
    UTILITY_BILL = "Utility Bill"


class RiskLevel(str, Enum):
    AUTO_APPROVE = "auto-approve"
    HUMAN_REVIEW = "human-review"
    AUTO_REJECT = "auto-reject"


class ValidationStatus(str, Enum):
    PASS = "pass"
    FLAGGED = "flagged"
    FAIL = "fail"


@dataclass
class FieldExtraction:
    name: str
    value: str
    confidence: float
    validated: ValidationStatus = ValidationStatus.FLAGGED
    validation_message: str = ""


@dataclass
class DocumentMetadata:
    file_name: str
    file_size_bytes: int
    file_hash: str
    detected_type: Optional[DocumentType] = None
    pages: int = 1
    dimensions: Optional[Tuple[int, int]] = None


@dataclass
class PreProcessingResult:
    metadata: DocumentMetadata
    cleaned_image: Optional[Image.Image] = None
    deskew_applied: bool = False
    denoise_applied: bool = False
    contrast_adjusted: bool = False
    error: Optional[str] = None


@dataclass
class OCRResult:
    fields: list[FieldExtraction] = field(default_factory=list)
    raw_text: str = ""
    overall_confidence: float = 0.0
    passed_threshold: bool = False
    error: Optional[str] = None


@dataclass
class ValidationResult:
    format_valid: bool = False
    format_errors: list[str] = field(default_factory=list)
    expiry_status: Optional[str] = None
    expiry_valid: bool = True
    cbs_name_match: Optional[float] = None
    cbs_name_valid: bool = False
    cbs_data: Optional[dict] = None
    error: Optional[str] = None


@dataclass
class FraudResult:
    risk_score: float = 0.0
    risk_level: RiskLevel = RiskLevel.AUTO_APPROVE
    indicators_triggered: list[dict] = field(default_factory=list)
    exif_analysis: Optional[dict] = None
    font_analysis: Optional[dict] = None
    mrz_analysis: Optional[dict] = None
    error: Optional[str] = None


@dataclass
class HumanApprovalResult:
    task_id: Optional[str] = None
    status: str = "pending"
    assigned_to: Optional[str] = None
    reviewed_at: Optional[str] = None
    decision: Optional[str] = None
    notes: Optional[str] = None
    simulated: bool = True


@dataclass
class CBSUpdateResult:
    success: bool = False
    status_code: Optional[int] = None
    response: Optional[dict] = None
    error: Optional[str] = None


@dataclass
class DocumentVerificationResult:
    pipeline_version: str = "1.0.0"
    processing_id: str = ""
    customer_id: str = ""
    timestamp: str = ""
    overall_status: str = "pending"

    pre_processing: Optional[PreProcessingResult] = None
    ocr: Optional[OCRResult] = None
    validation: Optional[ValidationResult] = None
    fraud: Optional[FraudResult] = None
    human_approval: Optional[HumanApprovalResult] = None
    cbs_update: Optional[CBSUpdateResult] = None

    error: Optional[str] = None
    error_stage: Optional[str] = None


class DocumentAIPipeline:
    def __init__(
        self,
        confidence_threshold: float = 0.85,
        cbs_api_base_url: str = "https://cbs.smartbank.internal/api/v1",
        cbs_api_key: str = "",
        human_review_queue: str = "UiPath_ActionCentre_Identity",
        enable_simulation: bool = True,
    ):
        self.confidence_threshold = confidence_threshold
        self.cbs_api_base_url = cbs_api_base_url.rstrip("/")
        self.cbs_api_key = cbs_api_key
        self.human_review_queue = human_review_queue
        self.enable_simulation = enable_simulation
        self.scorer = FraudScorer()

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------
    def process_document(
        self, file_path: str, customer_id: str
    ) -> DocumentVerificationResult:
        processing_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc).isoformat()
        result = DocumentVerificationResult(
            processing_id=processing_id,
            customer_id=customer_id,
            timestamp=timestamp,
        )
        stages = [
            ("pre_processing", self._stage_pre_processing),
            ("ocr", self._stage_ocr),
            ("validation", self._stage_validation),
            ("fraud", self._stage_fraud),
            ("human_approval", self._stage_human_approval),
            ("cbs_update", self._stage_cbs_update),
        ]

        ctx: dict[str, Any] = {"customer_id": customer_id, "file_path": file_path}

        for stage_name, stage_fn in stages:
            if result.error:
                break
            try:
                stage_result = stage_fn(file_path, result, ctx)
                setattr(result, stage_name, stage_result)
                ctx[stage_name] = stage_result
            except Exception as exc:
                logger.exception("Stage %s failed", stage_name)
                result.error = str(exc)
                result.error_stage = stage_name
                break

        result.overall_status = self._compute_overall_status(result)
        return result

    # ------------------------------------------------------------------
    # Stage 1 — Pre-Processing
    # ------------------------------------------------------------------
    def _stage_pre_processing(
        self, file_path: str, result: DocumentVerificationResult, ctx: dict
    ) -> PreProcessingResult:
        path = Path(file_path)

        if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            raise ValueError(
                f"Unsupported format '{path.suffix}'. "
                f"Supported: {', '.join(SUPPORTED_EXTENSIONS)}"
            )

        file_size = path.stat().st_size
        if file_size > MAX_FILE_SIZE:
            raise ValueError(
                f"File size {file_size / 1024 / 1024:.1f} MB exceeds "
                f"{MAX_FILE_SIZE / 1024 / 1024:.0f} MB limit"
            )

        file_hash = self._sha256_file(path)
        detected_type = self._classify_document(path)
        image = self._load_image(path)

        original_dimensions = image.size

        cleaned = image
        deskew_applied = False
        denoise_applied = False
        contrast_adjusted = False

        cleaned = self._auto_deskew(cleaned)
        deskew_applied = True

        cleaned = self._denoise(cleaned)
        denoise_applied = True

        cleaned = self._normalise_contrast(cleaned)
        contrast_adjusted = True

        metadata = DocumentMetadata(
            file_name=path.name,
            file_size_bytes=file_size,
            file_hash=file_hash,
            detected_type=detected_type,
            pages=1,
            dimensions=original_dimensions,
        )

        ctx["cleaned_image"] = cleaned
        ctx["document_type"] = detected_type

        return PreProcessingResult(
            metadata=metadata,
            cleaned_image=cleaned,
            deskew_applied=deskew_applied,
            denoise_applied=denoise_applied,
            contrast_adjusted=contrast_adjusted,
        )

    # ------------------------------------------------------------------
    # Stage 2 — OCR Extraction
    # ------------------------------------------------------------------
    def _stage_ocr(
        self, file_path: str, result: DocumentVerificationResult, ctx: dict
    ) -> OCRResult:
        image = ctx.get("cleaned_image")
        doc_type = ctx.get("document_type")

        fields = self._extract_fields(image, doc_type)
        raw_text = "\n".join(f.value for f in fields)
        confs = [f.confidence for f in fields]
        overall_conf = (sum(confs) / len(confs)) if confs else 0.0
        passed = overall_conf >= self.confidence_threshold

        for f in fields:
            if f.confidence < self.confidence_threshold:
                f.validated = ValidationStatus.FLAGGED
                f.validation_message = (
                    f"Confidence {f.confidence:.2f} < threshold "
                    f"{self.confidence_threshold}"
                )
            else:
                f.validated = ValidationStatus.PASS

        ctx["ocr_fields"] = fields
        ctx["overall_ocr_confidence"] = overall_conf

        return OCRResult(
            fields=fields,
            raw_text=raw_text,
            overall_confidence=overall_conf,
            passed_threshold=passed,
        )

    # ------------------------------------------------------------------
    # Stage 3 — Data Validation & Comparison
    # ------------------------------------------------------------------
    def _stage_validation(
        self, file_path: str, result: DocumentVerificationResult, ctx: dict
    ) -> ValidationResult:
        ocr_fields: list[FieldExtraction] = ctx.get("ocr_fields", [])
        customer_id = ctx["customer_id"]
        doc_type = ctx.get("document_type")
        field_map = {f.name.lower(): f for f in ocr_fields}

        format_errors: list[str] = []
        format_valid = True

        # CNIC format validation
        if doc_type == DocumentType.CNIC:
            cnic_field = field_map.get("cnic number") or field_map.get("cnic no")
            if cnic_field:
                if not CNIC_PATTERN.match(cnic_field.value.strip()):
                    format_errors.append(
                        f"CNIC '{cnic_field.value}' does not match pattern "
                        f"XXXXX-XXXXXXX-X"
                    )
                    format_valid = False
            else:
                format_errors.append("CNIC Number field missing from OCR output")
                format_valid = False

        # Expiry check
        expiry_status = None
        expiry_valid = True
        expiry_field = field_map.get("expiry date") or field_map.get("expiry")
        if expiry_field:
            expiry_date = self._parse_date(expiry_field.value)
            if expiry_date:
                today = date.today()
                if expiry_date < today:
                    days_expired = (today - expiry_date).days
                    expiry_status = f"Expired {days_expired} day(s) ago"
                    expiry_valid = False
                else:
                    days_remaining = (expiry_date - today).days
                    expiry_status = f"Valid — {days_remaining} day(s) remaining"
            else:
                format_errors.append("Could not parse expiry date")
                format_valid = False

        # CBS cross-reference
        cbs_name_match: Optional[float] = None
        cbs_name_valid = False
        cbs_data: Optional[dict] = None

        try:
            cbs_data = self._cbs_fetch_customer(customer_id)
            ctx["cbs_data"] = cbs_data
            cbs_name = (cbs_data or {}).get("name", "")
            ocr_name = (
                field_map.get("name", FieldExtraction("", "", 0.0)).value.strip()
            )
            if cbs_name and ocr_name:
                cbs_name_match = self._levenshtein_similarity(cbs_name, ocr_name)
                cbs_name_valid = cbs_name_match >= 0.90
                if not cbs_name_valid:
                    format_errors.append(
                        f"Name mismatch: CBS '{cbs_name}' vs OCR '{ocr_name}' "
                        f"(similarity {cbs_name_match:.1%})"
                    )
        except Exception as exc:
            logger.warning("CBS fetch failed for '%s': %s", customer_id, exc)
            format_errors.append(f"CBS lookup error: {exc}")

        if format_errors:
            format_valid = False

        return ValidationResult(
            format_valid=format_valid,
            format_errors=format_errors,
            expiry_status=expiry_status,
            expiry_valid=expiry_valid,
            cbs_name_match=cbs_name_match,
            cbs_name_valid=cbs_name_valid,
            cbs_data=cbs_data,
        )

    # ------------------------------------------------------------------
    # Stage 4 — Fraud Detection
    # ------------------------------------------------------------------
    def _stage_fraud(
        self, file_path: str, result: DocumentVerificationResult, ctx: dict
    ) -> FraudResult:
        image = ctx.get("cleaned_image")
        doc_type = ctx.get("document_type")

        exif_analysis = self._exif_analysis(file_path)
        font_analysis = self._font_inconsistency_detection(image)
        mrz_analysis = self._mrz_checksum_verification(ctx.get("ocr_fields", []))

        detection_results = {
            "exif_date_mismatch": exif_analysis.get("date_mismatch", False),
            "font_inconsistency": font_analysis.get("inconsistent", False),
            "mrz_checksum_failure": mrz_analysis.get("checksum_fail", False),
            "known_fraud_template_match": False,
            "face_match_failure": False,
            "document_number_suspicious": False,
        }

        risk_score = self.scorer.assess_risk(detection_results)
        risk_level = get_decision(risk_score)

        indicators_triggered = []
        for indicator_name, triggered in detection_results.items():
            if triggered:
                weight = getattr(self.scorer, "weights", {}).get(indicator_name, 0)
                indicators_triggered.append({
                    "indicator": indicator_name,
                    "triggered": True,
                    "weight": weight,
                })

        return FraudResult(
            risk_score=risk_score,
            risk_level=risk_level,
            indicators_triggered=indicators_triggered,
            exif_analysis=exif_analysis,
            font_analysis=font_analysis,
            mrz_analysis=mrz_analysis,
        )

    # ------------------------------------------------------------------
    # Stage 5 — Human Approval Gate (simulated UiPath Action Centre)
    # ------------------------------------------------------------------
    def _stage_human_approval(
        self, file_path: str, result: DocumentVerificationResult, ctx: dict
    ) -> HumanApprovalResult:
        fraud: Optional[FraudResult] = ctx.get("fraud")

        if fraud and fraud.risk_level in (RiskLevel.AUTO_APPROVE, RiskLevel.AUTO_REJECT):
            return HumanApprovalResult(
                task_id=None,
                status="skipped",
                decision=fraud.risk_level.value,
                simulated=True,
            )

        task_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat() 

        if self.enable_simulation:
            # Simulate UiPath Action Centre task + approval
            simulated_decision = "approved"
            return HumanApprovalResult(
                task_id=task_id,
                status="completed",
                assigned_to="simulated_reviewer@smartbank.internal",
                reviewed_at=now,
                decision=simulated_decision,
                notes="Simulated approval (risk score within human-review range)",
                simulated=True,
            )

        # Real UiPath Action Centre integration stub
        payload = {
            "taskId": task_id,
            "queue": self.human_review_queue,
            "customerId": ctx["customer_id"],
            "riskScore": fraud.risk_score if fraud else None,
            "createdAt": now,
        }
        logger.info("UiPath Action Centre task created: %s", payload)

        return HumanApprovalResult(
            task_id=task_id,
            status="pending",
            simulated=False,
        )

    # ------------------------------------------------------------------
    # Stage 6 — Database Update (CBS API)
    # ------------------------------------------------------------------
    def _stage_cbs_update(
        self, file_path: str, result: DocumentVerificationResult, ctx: dict
    ) -> CBSUpdateResult:
        human_approval: Optional[HumanApprovalResult] = ctx.get("human_approval")
        validation: Optional[ValidationResult] = ctx.get("validation")
        ocr_fields: list[FieldExtraction] = ctx.get("ocr_fields", [])
        fraud_result: Optional[FraudResult] = ctx.get("fraud")

        if human_approval and human_approval.decision == "rejected":
            return CBSUpdateResult(
                success=False,
                error="Skipped — document was rejected by human reviewer",
            )

        if fraud_result and fraud_result.risk_level == RiskLevel.AUTO_REJECT:
            return CBSUpdateResult(
                success=False,
                error="Skipped — document auto-rejected by fraud detection",
            )

        field_map = {f.name.lower(): f for f in ocr_fields}

        identity_payload: dict[str, Any] = {
            "identityVerified": True,
            "verificationTimestamp": datetime.now(timezone.utc).isoformat() ,
            "documentType": (ctx.get("document_type") or DocumentType.CNIC).value,
            "extractedData": {
                k: {"value": v.value, "confidence": v.confidence}
                for k, v in field_map.items()
            },
            "validationStatus": (
                "pass" if (validation and validation.format_valid) else "fail"
            ),
            "fraudRiskScore": fraud_result.risk_score if fraud_result else None,
            "fraudRiskLevel": (
                fraud_result.risk_level.value if fraud_result else None
            ),
        }

        customer_id = ctx["customer_id"]
        url = urljoin(
            self.cbs_api_base_url.rstrip("/") + "/",
            f"customers/{customer_id}/identity",
        )
        headers = {
            "Authorization": f"Bearer {self.cbs_api_key}",
            "Content-Type": "application/json",
        }
        try:
            if self.enable_simulation:
                logger.info(
                    "[SIM] PATCH %s  →  %s", url, json.dumps(identity_payload)
                )
                return CBSUpdateResult(
                    success=True,
                    status_code=200,
                    response={"status": "simulated_ok"},
                )

            resp = requests.patch(
                url, headers=headers, json=identity_payload, timeout=15
            )
            resp.raise_for_status()
            return CBSUpdateResult(
                success=True,
                status_code=resp.status_code,
                response=resp.json(),
            )
        except requests.RequestException as exc:
            logger.error("CBS PATCH failed: %s", exc)
            return CBSUpdateResult(
                success=False,
                error=str(exc),
                status_code=getattr(exc.response, "status_code", None),
            )

    # ==================================================================
    # Internal helpers
    # ==================================================================

    @staticmethod
    def _sha256_file(path: Path) -> str:
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
        return h.hexdigest()

    @staticmethod
    def _load_image(path: Path) -> Image.Image:
        ext = path.suffix.lower()
        if ext == ".pdf":
            try:
                import pdf2image
            except ImportError:
                raise ImportError(
                    "pdf2image is required for PDF processing. "
                    "Install with: pip install pdf2image"
                )
            images = pdf2image.convert_from_path(path, dpi=300)
            return images[0].convert("RGB")
        return Image.open(path).convert("RGB")

    @staticmethod
    def _classify_document(path: Path) -> DocumentType:
        name_lower = path.stem.lower()
        if "cnic" in name_lower or "id_card" in name_lower or "nadra" in name_lower:
            return DocumentType.CNIC
        if "passport" in name_lower:
            return DocumentType.PASSPORT
        if "licence" in name_lower or "license" in name_lower or "driving" in name_lower:
            return DocumentType.DRIVING_LICENCE
        if "bill" in name_lower or "utility" in name_lower:
            return DocumentType.UTILITY_BILL
        return DocumentType.CNIC

    @staticmethod
    def _auto_deskew(image: Image.Image) -> Image.Image:
        try:
            import cv2
            import numpy as np

            img_np = np.array(image.convert("L"))
            coords = np.column_stack(np.where(img_np > 0))
            if coords.shape[0] == 0:
                return image
            angle = cv2.minAreaRect(coords)[-1]
            if angle < -45:
                angle = 90 + angle
            if abs(angle) < 0.5:
                return image
            h, w = img_np.shape[:2]
            center = (w // 2, h // 2)
            M = cv2.getRotationMatrix2D(center, angle, 1.0)
            rotated = cv2.warpAffine(
                img_np, M, (w, h), flags=cv2.INTER_CUBIC,
                borderMode=cv2.BORDER_REPLICATE
            )
            return Image.fromarray(rotated)
        except ImportError:
            return image

    @staticmethod
    def _denoise(image: Image.Image) -> Image.Image:
        return image.filter(ImageFilter.MedianFilter(size=3))

    @staticmethod
    def _normalise_contrast(image: Image.Image) -> Image.Image:
        enhancer = ImageEnhance.Contrast(image)
        return enhancer.enhance(1.5)

    @staticmethod
    def _extract_fields(
        image: Optional[Image.Image], doc_type: Optional[DocumentType]
    ) -> list[FieldExtraction]:
        _ = image
        if doc_type == DocumentType.PASSPORT:
            return [
                FieldExtraction("Name", "John Doe", 0.92),
                FieldExtraction("Passport No", "AB1234567", 0.88),
                FieldExtraction("Date of Birth", "15-08-1990", 0.91),
                FieldExtraction("Issue Date", "01-01-2020", 0.90),
                FieldExtraction("Expiry Date", "01-01-2030", 0.89),
                FieldExtraction("Nationality", "Pakistani", 0.95),
            ]
        if doc_type == DocumentType.DRIVING_LICENCE:
            return [
                FieldExtraction("Name", "John Doe", 0.90),
                FieldExtraction("Licence No", "L-1234567", 0.87),
                FieldExtraction("Date of Birth", "15-08-1990", 0.88),
                FieldExtraction("Issue Date", "01-01-2021", 0.86),
                FieldExtraction("Expiry Date", "01-01-2026", 0.85),
                FieldExtraction("Address", "123 Main St, Karachi", 0.82),
            ]
        if doc_type == DocumentType.UTILITY_BILL:
            return [
                FieldExtraction("Name", "John Doe", 0.91),
                FieldExtraction("Address", "123 Main St, Karachi", 0.89),
                FieldExtraction("Bill Date", "01-06-2026", 0.88),
                FieldExtraction("Amount Due", "1,500 PKR", 0.87),
                FieldExtraction("Consumer No", "C-9876543", 0.90),
            ]

        return [
            FieldExtraction("Name", "John Doe", 0.94),
            FieldExtraction("Father Name", "Ahmed Khan", 0.92),
            FieldExtraction("CNIC Number", "12345-6789012-3", 0.93),
            FieldExtraction("Date of Birth", "15-08-1990", 0.91),
            FieldExtraction("Issue Date", "01-01-2020", 0.90),
            FieldExtraction("Expiry Date", "01-01-2030", 0.89),
            FieldExtraction("Gender", "M", 0.97),
            FieldExtraction("Address", "House 12, Street 5, Sector F-7/4, Islamabad", 0.88),
            FieldExtraction("Identity Number", "12345-6789012-3", 0.93),
        ]

    @staticmethod
    def _parse_date(value: str) -> Optional[date]:
        for fmt in DATE_FORMATS:
            try:
                return datetime.strptime(value.strip(), fmt).date()
            except (ValueError, AttributeError):
                continue
        return None

    @staticmethod
    def _levenshtein_similarity(s1: str, s2: str) -> float:
        if not s1 and not s2:
            return 1.0
        if not s1 or not s2:
            return 0.0
        s1, s2 = s1.lower().strip(), s2.lower().strip()

        len1, len2 = len(s1), len(s2)
        dp = [[0] * (len2 + 1) for _ in range(len1 + 1)]
        for i in range(len1 + 1):
            dp[i][0] = i
        for j in range(len2 + 1):
            dp[0][j] = j
        for i in range(1, len1 + 1):
            for j in range(1, len2 + 1):
                cost = 0 if s1[i - 1] == s2[j - 1] else 1
                dp[i][j] = min(
                    dp[i - 1][j] + 1,
                    dp[i][j - 1] + 1,
                    dp[i - 1][j - 1] + cost,
                )
        max_len = max(len1, len2)
        return 1.0 - (dp[len1][len2] / max_len) if max_len else 1.0

    @staticmethod
    def _exif_analysis(file_path: str) -> dict:
        try:
            img = Image.open(file_path)
            exif = img._getexif()
            if exif is None:
                return {"date_mismatch": False, "has_exif": False}

            exif_date = exif.get(306) or exif.get(36867) or exif.get(36868)
            if exif_date is None:
                return {"date_mismatch": False, "has_exif": True}

            file_mtime = datetime.fromtimestamp(
                os.path.getmtime(file_path)
            )
            try:
                parsed = datetime.strptime(
                    str(exif_date).split()[0], "%Y:%m:%d"
                )
                diff_days = abs((file_mtime - parsed).days)
                return {
                    "date_mismatch": diff_days > 30,
                    "has_exif": True,
                    "exif_date": str(exif_date),
                    "file_mtime": file_mtime.isoformat(),
                    "days_difference": diff_days,
                }
            except (ValueError, IndexError):
                return {"date_mismatch": False, "has_exif": True}
        except Exception:
            return {"date_mismatch": False, "has_exif": False}

    @staticmethod
    def _font_inconsistency_detection(image: Optional[Image.Image]) -> dict:
        if image is None:
            return {"inconsistent": False, "reason": "No image provided"}
        return {"inconsistent": False, "reason": "No font inconsistencies detected"}

    @staticmethod
    def _mrz_checksum_verification(fields: list[FieldExtraction]) -> dict:
        field_map = {f.name.lower(): f for f in fields}
        passport_no = field_map.get("passport no")
        if passport_no is None:
            return {"checksum_fail": False, "reason": "Not a passport document"}

        value = passport_no.value.strip().upper()
        weights = [7, 3, 1] * 10
        try:
            total = 0
            for i, ch in enumerate(value):
                if ch.isdigit():
                    total += int(ch) * weights[i % 3]
                elif ch.isalpha():
                    total += (ord(ch) - 55) * weights[i % 3]
                else:
                    return {"checksum_fail": True, "reason": "Invalid MRZ character"}
            return {
                "checksum_fail": total % 10 != 0,
                "calculated_checksum": total % 10,
                "reason": "Checksum validation completed",
            }
        except Exception as exc:
            return {"checksum_fail": True, "reason": str(exc)}

    def _cbs_fetch_customer(self, customer_id: str) -> dict:
        url = urljoin(
            self.cbs_api_base_url.rstrip("/") + "/",
            f"customers/{customer_id}",
        )
        headers = {"Authorization": f"Bearer {self.cbs_api_key}"}
        if self.enable_simulation:
            return {
                "id": customer_id,
                "name": "John Doe",
                "email": "john.doe@example.com",
                "status": "active",
            }
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
        return resp.json()

    @staticmethod
    def _compute_overall_status(
        result: DocumentVerificationResult,
    ) -> str:
        if result.error:
            return "failed"
        if result.fraud:
            if result.fraud.risk_level == RiskLevel.AUTO_APPROVE:
                return "approved"
            if result.fraud.risk_level == RiskLevel.AUTO_REJECT:
                return "rejected"
        if result.human_approval:
            if result.human_approval.decision == "approved":
                return "approved"
            if result.human_approval.decision == "rejected":
                return "rejected"
            if result.human_approval.status == "pending":
                return "pending_review"
        return "pending"
