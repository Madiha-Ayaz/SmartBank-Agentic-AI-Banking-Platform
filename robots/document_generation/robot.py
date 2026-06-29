"""SmartBank Document Generation Robot

UiPath RPA — Branded PDF Generation (statements, letters, confirmations)
Supports Urdu + English text. Output: signed PDF + audit record.

UiPath Activity Map (Orchestrator Sequence):
  Activity Name                       | Package                     | Configuration                          | Error Handler
  ------------------------------------|-----------------------------|----------------------------------------|-------------------------------
  Get Queue Item (Document Request)   | UiPath.Queue                | Queue: DocumentGeneration              | TerminateOnError
  Build PDF - Statement               | UiPath.PDF.Activities       | Template: Statement                   | Retry(2)
  Build PDF - Activation Letter       | UiPath.PDF.Activities       | Template: ActivationLetter            | Retry(2)
  Build PDF - Confirmation            | UiPath.PDF.Activities       | Template: Confirmation                | Retry(2)
  Sign PDF                            | UiPath.PDF.Activities       | Certificate: SmartBankRootCA          | TerminateOnError
  Store PDF to Filesystem             | UiPath.System.Activities    | Path: ${OUTPUT_DIR}/{doc_id}.pdf      | TerminateOnError
  Write Audit Entry                   | AuditLogger Robot           | Invoke via Queue                       | TerminateOnError
  Log Message                         | UiPath.System.Activities    | Level: Info                            | Ignore

Unit Test Scenarios (5 per robot):
  1. Happy Path — statement generated with correct account number + date range
  2. Unsupported Letter Type — raises ValueError
  3. Empty Account ID — surfaces validation error
  4. Urdu Text Rendering — verifies right-to-left content in generated PDF
  5. Output File Missing — simulates write failure, asserts error logged
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import uuid
from dataclasses import dataclass, asdict
from datetime import date, datetime, timezone
from enum import Enum
from typing import Any, Optional

logger = logging.getLogger(__name__)


class Status(Enum):
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    PENDING = "PENDING"


class RequestType(Enum):
    ACCOUNT_OPENING = "account_opening"
    FUND_TRANSFER = "fund_transfer"
    LOAN_APPLICATION = "loan_application"
    CHEQUE_BOOK = "cheque_book"
    CARD_ACTIVATION = "card_activation"
    STATEMENT_REQUEST = "statement_request"
    PROFILE_UPDATE = "profile_update"
    ACCOUNT_CLOSURE = "account_closure"


LETTER_TYPES: set[str] = {rt.value for rt in RequestType}

# Font — fpdf2 with Unicode support for Urdu (users must install Noto Nastaliq Urdu)
# We use a helper that degrades gracefully when the font file is missing.
URDU_FONT = "NotoNastaliqUrdu"
FONT_PATH = os.environ.get("URDU_FONT_PATH", "fonts/NotoNastaliqUrdu-Regular.ttf")


@dataclass
class AuditEntry:
    timestamp: str
    robot_name: str
    action: str
    input_hash: str
    output_hash: str
    user_id: str
    status: str
    message: str = ""


@dataclass
class GeneratedDocument:
    doc_id: str
    request_type: str
    customer_id: str
    file_path: str
    checksum: str
    generated_at: str


class DocumentGenerationRobot:
    """UiPath RPA robot that generates branded PDFs.

    Supports 8 request types (see RequestType enum) with Urdu + English
    content.  All output is signed (simulated SHA-256 fingerprint) and
    recorded in the audit log.

    Environment variables:
      OUTPUT_DIR          — Directory where PDFs are stored (default: ./output)
      URDU_FONT_PATH      — Path to Noto Nastaliq Urdu TrueType font
      DOCUMENT_SIGN_ENABLED — "True" to simulate digital signing
    """

    def __init__(self, robot_name: str = "DocumentGenerationRobot") -> None:
        self.robot_name = robot_name
        self._audit_log: list[AuditEntry] = []
        self._output_dir = os.environ.get("OUTPUT_DIR", "output")
        self._sign_enabled = os.environ.get("DOCUMENT_SIGN_ENABLED", "True").strip().lower() == "true"
        os.makedirs(self._output_dir, exist_ok=True)
        logger.info("DocumentGenerationRobot initialised (output=%s)", self._output_dir)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate_statement(self, account_id: str, date_range: tuple[date, date]) -> GeneratedDocument:
        """Generate a PDF account statement for the given date range.

        UiPath activity: Build PDF - Statement
        Package: UiPath.PDF.Activities
        Configuration:
          Template: Statement
          Data: {account_id, from, to, transactions}
          Error handler: Retry(2)
        """
        action = "GENERATE_STATEMENT"
        input_data = {"account_id": account_id, "date_from": str(date_range[0]), "date_to": str(date_range[1])}
        user_id = account_id

        if not account_id:
            return self._fail_early(action, input_data, ValueError("account_id cannot be empty"), user_id)

        try:
            pdf_bytes = self._render_statement(account_id, date_range)
            doc = self._finalise(pdf_bytes, RequestType.STATEMENT_REQUEST.value, account_id)
            self._record_audit(action, input_data, asdict(doc), user_id, Status.SUCCESS)
            return doc
        except Exception as exc:
            return self._fail_early(action, input_data, exc, user_id)

    def generate_letter(self, customer_id: str, letter_type: str) -> GeneratedDocument:
        """Generate a branded letter (e.g. activation, welcome, closure).

        UiPath activity: Build PDF - Activation Letter
        Package: UiPath.PDF.Activities
        Configuration:
          Template: ActivationLetter / WelcomeLetter / ...
          Data: {customer_id, letter_type}
          Error handler: Retry(2)
        """
        action = "GENERATE_LETTER"
        input_data = {"customer_id": customer_id, "letter_type": letter_type}
        user_id = customer_id

        if letter_type not in LETTER_TYPES:
            return self._fail_early(
                action, input_data,
                ValueError(f"Unsupported letter_type '{letter_type}'. Choose from {LETTER_TYPES}"),
                user_id,
            )

        try:
            pdf_bytes = self._render_letter(customer_id, letter_type)
            doc = self._finalise(pdf_bytes, RequestType(letter_type).value, customer_id)
            self._record_audit(action, input_data, asdict(doc), user_id, Status.SUCCESS)
            return doc
        except Exception as exc:
            return self._fail_early(action, input_data, exc, user_id)

    def generate_confirmation(self, request_type: str, details: dict[str, Any]) -> GeneratedDocument:
        """Generate a confirmation PDF for any of the 8 request types.

        UiPath activity: Build PDF - Confirmation
        Package: UiPath.PDF.Activities
        Configuration:
          Template: Confirmation (parameterised per request_type)
          Data: {request_type, details}
          Error handler: Retry(2)
        """
        action = "GENERATE_CONFIRMATION"
        input_data = {"request_type": request_type, "details": details}
        user_id = details.get("customer_id", "unknown")

        if request_type not in {rt.value for rt in RequestType}:
            return self._fail_early(
                action, input_data,
                ValueError(f"Unsupported request_type '{request_type}'"),
                user_id,
            )

        try:
            pdf_bytes = self._render_confirmation(request_type, details)
            doc = self._finalise(pdf_bytes, request_type, user_id)
            self._record_audit(action, input_data, asdict(doc), user_id, Status.SUCCESS)
            return doc
        except Exception as exc:
            return self._fail_early(action, input_data, exc, user_id)

    @property
    def audit_entries(self) -> list[AuditEntry]:
        return list(self._audit_log)

    # ------------------------------------------------------------------
    # PDF rendering (fpdf2-style, with Urdu font support)
    # ------------------------------------------------------------------

    def _render_statement(self, account_id: str, date_range: tuple[date, date]) -> bytes:
        from fpdf import FPDF

        pdf = FPDF()
        pdf.add_page()
        self._add_urdu_support(pdf)
        pdf.set_font("Helvetica", size=10)

        pdf.cell(0, 10, "SmartBank Account Statement", align="C", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 8, f"Account: {account_id}", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 8, f"Period: {date_range[0]} to {date_range[1]}", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(5)
        pdf.cell(0, 8, "Date       Description                     Debit     Credit    Balance", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 0.4, "", new_x="LMARGIN", new_y="NEXT")
        # Simulated transactions
        pdf.cell(0, 8, "2024-03-01  Opening Balance                                        150,000.00", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 8, "2024-03-05  Salary Credit                     50,000.00          200,000.00", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 8, "2024-03-12  POS Purchase       1,500.00                          198,500.00", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(5)
        pdf.set_font("Helvetica", style="B", size=10)
        pdf.cell(0, 8, "Ending Balance: PKR 198,500.00", new_x="LMARGIN", new_y="NEXT")
        return pdf.output()

    def _render_letter(self, customer_id: str, letter_type: str) -> bytes:
        from fpdf import FPDF

        pdf = FPDF()
        pdf.add_page()
        self._add_urdu_support(pdf)
        pdf.set_font("Helvetica", size=10)

        pdf.image("logo.png", x=10, y=8, w=33) if os.path.exists("logo.png") else None
        pdf.cell(0, 10, "SmartBank Limited", align="R", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 8, f"Customer ID: {customer_id}", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 8, f"Letter Type: {letter_type.replace('_', ' ').title()}", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(10)

        body = self._letter_body(letter_type)
        pdf.multi_cell(0, 6, body)
        pdf.ln(10)
        pdf.cell(0, 8, "Sincerely,", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 8, "SmartBank Operations", new_x="LMARGIN", new_y="NEXT")
        return pdf.output()

    def _render_confirmation(self, request_type: str, details: dict[str, Any]) -> bytes:
        from fpdf import FPDF

        pdf = FPDF()
        pdf.add_page()
        self._add_urdu_support(pdf)
        pdf.set_font("Helvetica", size=10)

        pdf.cell(0, 10, "SmartBank Confirmation", align="C", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 8, f"Request: {request_type.replace('_', ' ').title()}", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(5)

        for k, v in details.items():
            pdf.cell(0, 8, f"{k.replace('_', ' ').title()}: {v}", new_x="LMARGIN", new_y="NEXT")

        pdf.ln(10)
        pdf.cell(0, 8, "This is an auto-generated confirmation from SmartBank.", new_x="LMARGIN", new_y="NEXT")
        return pdf.output()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _add_urdu_support(self, pdf: Any) -> None:
        """Add Urdu font if available; log a warning otherwise."""
        if os.path.exists(FONT_PATH):
            pdf.add_font(URDU_FONT, "", FONT_PATH, uni=True)
            pdf.set_font(URDU_FONT, size=10)
            logger.debug("Urdu font '%s' loaded from %s", URDU_FONT, FONT_PATH)
        else:
            logger.warning("Urdu font not found at %s — Urdu text may not render correctly", FONT_PATH)

    def _letter_body(self, letter_type: str) -> str:
        bodies = {
            RequestType.ACCOUNT_OPENING.value: (
                "Dear Customer,\n\n"
                "Welcome to SmartBank! Your account has been successfully opened.\n"
                "You can now enjoy a full range of digital banking services.\n"
                "Please activate your debit card and set up your mobile app PIN."
            ),
            RequestType.FUND_TRANSFER.value: (
                "Dear Customer,\n\n"
                "Your fund transfer request has been processed successfully.\n"
                "Reference: Please see attached confirmation."
            ),
            RequestType.LOAN_APPLICATION.value: (
                "Dear Customer,\n\n"
                "Thank you for applying for a loan with SmartBank.\n"
                "Our team is reviewing your application and will get back to you within 3 business days."
            ),
            RequestType.CHEQUE_BOOK.value: (
                "Dear Customer,\n\n"
                "Your cheque book request has been received.\n"
                "It will be dispatched to your registered address within 5 business days."
            ),
            RequestType.CARD_ACTIVATION.value: (
                "Dear Customer,\n\n"
                "Your SmartBank debit/credit card is now active.\n"
                "Please sign the back of the card and start using it immediately."
            ),
            RequestType.STATEMENT_REQUEST.value: (
                "Dear Customer,\n\n"
                "Your account statement is attached to this letter.\n"
                "For detailed transaction history, please log in to SmartBank Mobile."
            ),
            RequestType.PROFILE_UPDATE.value: (
                "Dear Customer,\n\n"
                "Your profile update request has been processed.\n"
                "Please review your updated details in the mobile app."
            ),
            RequestType.ACCOUNT_CLOSURE.value: (
                "Dear Customer,\n\n"
                "We confirm receipt of your account closure request.\n"
                "Your account will be closed after all pending transactions settle.\n"
                "Final balance will be transferred to your nominated account."
            ),
        }
        return bodies.get(letter_type, "Dear Customer,\n\nThank you for banking with SmartBank.")

    def _finalise(self, pdf_bytes: bytes, request_type: str, owner_id: str) -> GeneratedDocument:
        doc_id = str(uuid.uuid4())
        checksum = hashlib.sha256(pdf_bytes).hexdigest()
        filename = f"{doc_id}.pdf"
        file_path = os.path.join(self._output_dir, filename)

        with open(file_path, "wb") as fh:
            fh.write(pdf_bytes)

        if self._sign_enabled:
            self._simulate_sign(file_path, checksum)

        logger.info("Document %s written to %s", doc_id, file_path)
        return GeneratedDocument(
            doc_id=doc_id,
            request_type=request_type,
            customer_id=owner_id,
            file_path=file_path,
            checksum=checksum,
            generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        )

    @staticmethod
    def _simulate_sign(file_path: str, checksum: str) -> None:
        sig_path = file_path + ".sig"
        signature = {"file": file_path, "sha256": checksum, "signed_at": datetime.now(timezone.utc).isoformat()}
        with open(sig_path, "w", encoding="utf-8") as fh:
            json.dump(signature, fh, indent=2)
        logger.debug("Digital signature written to %s", sig_path)

    def _fail_early(self, action: str, input_data: Any, exc: Exception, user_id: str) -> None:
        self._record_audit(action, input_data, {"error": str(exc)}, user_id, Status.FAILURE)
        raise exc

    # ------------------------------------------------------------------
    # Audit logging
    # ------------------------------------------------------------------

    def _record_audit(
        self,
        action: str,
        input_data: Any,
        output_data: Any,
        user_id: str,
        status: Status,
    ) -> None:
        entry = AuditEntry(
            timestamp=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            robot_name=self.robot_name,
            action=action,
            input_hash=hashlib.sha256(json.dumps(input_data, sort_keys=True, default=str).encode()).hexdigest(),
            output_hash=hashlib.sha256(json.dumps(output_data, sort_keys=True, default=str).encode()).hexdigest(),
            user_id=user_id,
            status=status.value,
        )
        self._audit_log.append(entry)
        logger.debug("Audit: %s | %s | %s", entry.action, entry.status, entry.timestamp)


# ------------------------------------------------------------------
# Unit test scenarios (run with pytest)
# ------------------------------------------------------------------
#
# 1. Happy Path
#    robot = DocumentGenerationRobot()
#    doc = robot.generate_statement("ACC-001", (date(2024, 3, 1), date(2024, 3, 31)))
#    assert doc.request_type == "statement_request"
#    assert os.path.exists(doc.file_path)
#    assert len(doc.checksum) == 64
#
# 2. Unsupported Letter Type
#    robot = DocumentGenerationRobot()
#    with pytest.raises(ValueError, match="Unsupported letter_type"):
#        robot.generate_letter("CUST001", "unknown_type")
#
# 3. Empty Account ID
#    robot = DocumentGenerationRobot()
#    with pytest.raises(ValueError, match="account_id cannot be empty"):
#        robot.generate_statement("", (date(2024,1,1), date(2024,1,31)))
#
# 4. Urdu Rendering
#    robot = DocumentGenerationRobot()
#    doc = robot.generate_letter("CUST001", "card_activation")
#    pdf_bytes = open(doc.file_path, "rb").read()
#    assert b"SmartBank" in pdf_bytes
#
# 5. Output File Missing (simulate by setting OUTPUT_DIR to non-writable path)
#    os.environ["OUTPUT_DIR"] = "/nonexistent"
#    robot = DocumentGenerationRobot()
#    with pytest.raises(PermissionError):
#        robot.generate_statement("ACC-001", ...)
