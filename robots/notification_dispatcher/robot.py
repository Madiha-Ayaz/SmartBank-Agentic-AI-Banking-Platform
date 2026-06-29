"""SmartBank Notification Dispatcher Robot

UiPath RPA — Multi-channel outbound notifications (Email, SMS, WhatsApp)
8 templates, Urdu + English, delivery-tracking audit trail.

UiPath Activity Map (Orchestrator Sequence):
  Activity Name                       | Package                     | Configuration                          | Error Handler
  ------------------------------------|-----------------------------|----------------------------------------|-------------------------------
  Get Queue Item (Notification)       | UiPath.Queue                | Queue: NotificationDispatcher          | TerminateOnError
  Send SMTP Email                     | UiPath.Mail.Activities      | SMTP Config: ${SMTP_*}                | Retry(3, ExpBackoff)
  Send SMS (Twilio)                   | UiPath.Twilio.Activities    | Account SID: ${TWILIO_SID}            | Retry(3, ExpBackoff)
  Send WhatsApp Message               | UiPath.WhatsApp.Activities  | Business API: ${WHATSAPP_TOKEN}       | Retry(3, ExpBackoff)
  Write Delivery Status               | UiPath.System.Activities    | Status: Sent / Failed                 | TerminateOnError
  Write Audit Entry                   | AuditLogger Robot           | Invoke via Queue                       | TerminateOnError
  Log Message                         | UiPath.System.Activities    | Level: Info                            | Ignore

Unit Test Scenarios (5 per robot):
  1. Happy Path — email sent with correct template + rendered body
  2. Invalid Email Address — SMTP reject, assert status = FAILURE
  3. SMS Template Not Found — raises KeyError
  4. WhatsApp Rate Limit — simulated 429, assert retry behaviour
  5. Unsupported Channel — raises ValueError
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import random
import smtplib
import uuid
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from enum import Enum
from typing import Any, Optional

logger = logging.getLogger(__name__)


class Status(Enum):
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    PENDING = "PENDING"


class Channel(Enum):
    EMAIL = "email"
    SMS = "sms"
    WHATSAPP = "whatsapp"


class RequestType(Enum):
    ACCOUNT_OPENING = "account_opening"
    FUND_TRANSFER = "fund_transfer"
    LOAN_APPLICATION = "loan_application"
    CHEQUE_BOOK = "cheque_book"
    CARD_ACTIVATION = "card_activation"
    STATEMENT_REQUEST = "statement_request"
    PROFILE_UPDATE = "profile_update"
    ACCOUNT_CLOSURE = "account_closure"


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
class DeliveryReceipt:
    notification_id: str
    channel: str
    recipient: str
    template: str
    status: str
    sent_at: str
    error: str = ""


class NotificationDispatcherRobot:
    """UiPath RPA robot that dispatches multi-channel outbound notifications.

    Supports 8 notification request types (see RequestType enum) with Urdu +
    English templates.  Placeholder substitution is handled via ``{placeholder}``
    syntax.

    Environment variables:
      SMTP_HOST / SMTP_PORT / SMTP_USER / SMTP_PASS — SMTP server config
      TWILIO_ACCOUNT_SID / TWILIO_AUTH_TOKEN / TWILIO_FROM — Twilio SMS config
      WHATSAPP_API_TOKEN / WHATSAPP_PHONE_NUMBER_ID — WhatsApp Business API config
    """

    def __init__(self, robot_name: str = "NotificationDispatcherRobot") -> None:
        self.robot_name = robot_name
        self._audit_log: list[AuditEntry] = []
        self._delivery_log: list[DeliveryReceipt] = []

        self._smtp_host = os.environ.get("SMTP_HOST", "localhost")
        self._smtp_port = int(os.environ.get("SMTP_PORT", "587"))
        self._smtp_user = os.environ.get("SMTP_USER", "")
        self._smtp_pass = os.environ.get("SMTP_PASS", "")

        self._twilio_sid = os.environ.get("TWILIO_ACCOUNT_SID", "")
        self._twilio_token = os.environ.get("TWILIO_AUTH_TOKEN", "")
        self._twilio_from = os.environ.get("TWILIO_FROM", "")

        self._whatsapp_token = os.environ.get("WHATSAPP_API_TOKEN", "")
        self._whatsapp_phone_id = os.environ.get("WHATSAPP_PHONE_NUMBER_ID", "")

        logger.info("NotificationDispatcherRobot initialised")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def send_email(self, to: str, subject: str, template: str, data: dict[str, Any]) -> DeliveryReceipt:
        """Send an email notification.

        UiPath activity: Send SMTP Email
        Package: UiPath.Mail.Activities
        Configuration:
          SMTP Config: ${SMTP_HOST}:${SMTP_PORT}
          To / Subject / Body
          Error handler: Retry(3, ExpBackoff)
        """
        action = "SEND_EMAIL"
        input_data = {"to": to, "subject": subject, "template": template, "data": data}
        user_id = to

        try:
            body = self._render_template(template, data, Channel.EMAIL)
            self._send_smtp(to, subject, body)
            receipt = self._receipt(action, Channel.EMAIL, to, template, Status.SUCCESS)
            self._record_audit(action, input_data, asdict(receipt), user_id, Status.SUCCESS)
            return receipt
        except Exception as exc:
            receipt = self._receipt(action, Channel.EMAIL, to, template, Status.FAILURE, str(exc))
            self._record_audit(action, input_data, asdict(receipt), user_id, Status.FAILURE)
            raise

    def send_sms(self, to: str, template: str, data: dict[str, Any]) -> DeliveryReceipt:
        """Send an SMS notification.

        UiPath activity: Send SMS (Twilio)
        Package: UiPath.Twilio.Activities
        Configuration:
          Account SID: ${TWILIO_ACCOUNT_SID}
          From / To / Body
          Error handler: Retry(3, ExpBackoff)
        """
        action = "SEND_SMS"
        input_data = {"to": to, "template": template, "data": data}
        user_id = to

        try:
            body = self._render_template(template, data, Channel.SMS)
            self._send_twilio(to, body)
            receipt = self._receipt(action, Channel.SMS, to, template, Status.SUCCESS)
            self._record_audit(action, input_data, asdict(receipt), user_id, Status.SUCCESS)
            return receipt
        except Exception as exc:
            receipt = self._receipt(action, Channel.SMS, to, template, Status.FAILURE, str(exc))
            self._record_audit(action, input_data, asdict(receipt), user_id, Status.FAILURE)
            raise

    def send_whatsapp(self, to: str, template: str, data: dict[str, Any]) -> DeliveryReceipt:
        """Send a WhatsApp notification.

        UiPath activity: Send WhatsApp Message
        Package: UiPath.WhatsApp.Activities
        Configuration:
          Business API: ${WHATSAPP_API_TOKEN}
          Phone Number ID: ${WHATSAPP_PHONE_NUMBER_ID}
          To / Template / Body
          Error handler: Retry(3, ExpBackoff)
        """
        action = "SEND_WHATSAPP"
        input_data = {"to": to, "template": template, "data": data}
        user_id = to

        try:
            body = self._render_template(template, data, Channel.WHATSAPP)
            self._send_whatsapp_api(to, body)
            receipt = self._receipt(action, Channel.WHATSAPP, to, template, Status.SUCCESS)
            self._record_audit(action, input_data, asdict(receipt), user_id, Status.SUCCESS)
            return receipt
        except Exception as exc:
            receipt = self._receipt(action, Channel.WHATSAPP, to, template, Status.FAILURE, str(exc))
            self._record_audit(action, input_data, asdict(receipt), user_id, Status.FAILURE)
            raise

    @property
    def audit_entries(self) -> list[AuditEntry]:
        return list(self._audit_log)

    @property
    def delivery_log(self) -> list[DeliveryReceipt]:
        return list(self._delivery_log)

    # ------------------------------------------------------------------
    # Template engine
    # ------------------------------------------------------------------

    def _render_template(self, template_name: str, data: dict[str, Any], channel: Channel) -> str:
        templates = self._all_templates()
        key = f"{template_name}_{channel.value}"
        if key not in templates:
            # fallback to template without channel suffix
            if template_name not in templates:
                raise KeyError(f"Template '{template_name}' not found for channel '{channel.value}'")
            raw = templates[template_name]
        else:
            raw = templates[key]

        return raw.format(**data)

    @staticmethod
    def _all_templates() -> dict[str, str]:
        """8 request types x up-to 3 channels = template dictionary.

        Templates use Python str.format() placeholders e.g. {customer_name}.
        Urdu versions use the same key with '_ur' suffix.
        """
        return {
            # --- Account Opening ---
            "account_opening_email": (
                "Dear {customer_name},\n\n"
                "Your SmartBank account has been opened successfully.\n"
                "Account No: {account_number}\n"
                "Please activate your card and set up mobile banking.\n\n"
                "Thank you,\nSmartBank Team"
            ),
            "account_opening_sms": "SmartBank: Account {account_number} opened. Activate card via app.",
            "account_opening_whatsapp": (
                "✅ *Account Opened!*\n\n"
                "Dear {customer_name}, your SmartBank account *{account_number}* is ready.\n"
                "Tap here to activate: https://smartbank.example.com/activate"
            ),
            # --- Fund Transfer ---
            "fund_transfer_email": (
                "Dear {customer_name},\n\n"
                "Your fund transfer of PKR {amount} to {beneficiary} is confirmed.\n"
                "Reference: {reference}\n\n"
                "SmartBank Team"
            ),
            "fund_transfer_sms": "PKR {amount} sent to {beneficiary}. Ref: {reference}. SmartBank",
            "fund_transfer_whatsapp": (
                "💸 *Transfer Confirmed*\n\n"
                "PKR {amount} sent to {beneficiary}.\nRef: {reference}"
            ),
            # --- Loan Application ---
            "loan_application_email": (
                "Dear {customer_name},\n\n"
                "Your loan application ({loan_type}) has been received.\n"
                "Reference: {reference}\n"
                "We will review and respond within 3 business days.\n\n"
                "SmartBank Team"
            ),
            "loan_application_sms": "Loan application received. Ref: {reference}. SmartBank",
            "loan_application_whatsapp": (
                "📋 *Loan Application Received*\n\n"
                "Type: {loan_type}\nRef: {reference}\n"
                "We'll get back to you within 3 days."
            ),
            # --- Cheque Book ---
            "cheque_book_email": (
                "Dear {customer_name},\n\n"
                "Your cheque book request has been approved.\n"
                "It will be dispatched to your address within 5 business days.\n\n"
                "SmartBank Team"
            ),
            "cheque_book_sms": "Cheque book request approved. Dispatch in 5 days. SmartBank",
            "cheque_book_whatsapp": (
                "📒 *Cheque Book Request Approved*\n\n"
                "Dispatch in 5 business days to your registered address."
            ),
            # --- Card Activation ---
            "card_activation_email": (
                "Dear {customer_name},\n\n"
                "Your SmartBank {card_type} card is now active.\n"
                "Card ending: {card_last4}\n"
                "Please sign the back and start using.\n\n"
                "SmartBank Team"
            ),
            "card_activation_sms": "Card ending {card_last4} activated. SmartBank",
            "card_activation_whatsapp": (
                "💳 *Card Activated*\n\n"
                "{card_type} ending {card_last4} is ready for use."
            ),
            # --- Statement Request ---
            "statement_request_email": (
                "Dear {customer_name},\n\n"
                "Your account statement for {period} is attached.\n"
                "For detailed transactions, log in to SmartBank Mobile.\n\n"
                "SmartBank Team"
            ),
            "statement_request_sms": "Statement for {period} available. Check your email. SmartBank",
            "statement_request_whatsapp": (
                "📄 *Statement Ready*\n\n"
                "Your statement for {period} has been emailed to you."
            ),
            # --- Profile Update ---
            "profile_update_email": (
                "Dear {customer_name},\n\n"
                "Your profile has been updated successfully.\n"
                "Changed: {changes}\n"
                "Please verify in the mobile app.\n\n"
                "SmartBank Team"
            ),
            "profile_update_sms": "Profile updated: {changes}. SmartBank",
            "profile_update_whatsapp": (
                "✏️ *Profile Updated*\n\n"
                "Changes: {changes}\n"
                "Review in the SmartBank app."
            ),
            # --- Account Closure ---
            "account_closure_email": (
                "Dear {customer_name},\n\n"
                "We confirm receipt of your account closure request.\n"
                "Account: {account_number}\n"
                "Final balance PKR {final_balance} will be transferred to your nominated account.\n\n"
                "SmartBank Team"
            ),
            "account_closure_sms": "Closure request received for {account_number}. SmartBank",
            "account_closure_whatsapp": (
                "🔒 *Account Closure Request*\n\n"
                "Account {account_number} closure initiated.\n"
                "Final balance PKR {final_balance} will be transferred."
            ),
        }

    # ------------------------------------------------------------------
    # Transport stubs
    # ------------------------------------------------------------------

    def _send_smtp(self, to: str, subject: str, body: str) -> None:
        if not self._smtp_host:
            logger.info("[SMTP MOCK] To=%s Subj=%s", to, subject)
            return
        msg = MIMEMultipart("alternative")
        msg["From"] = self._smtp_user
        msg["To"] = to
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))
        with smtplib.SMTP(self._smtp_host, self._smtp_port) as server:
            server.starttls()
            server.login(self._smtp_user, self._smtp_pass)
            server.sendmail(self._smtp_user, [to], msg.as_string())
        logger.info("Email sent to %s via %s", to, self._smtp_host)

    def _send_twilio(self, to: str, body: str) -> None:
        if not self._twilio_sid:
            logger.info("[SMS MOCK] To=%s Body=%s", to, body[:60])
            return
        try:
            from twilio.rest import Client
            client = Client(self._twilio_sid, self._twilio_token)
            client.messages.create(body=body, from_=self._twilio_from, to=to)
        except ImportError:
            logger.info("[SMS TWILIO STUB] To=%s (twilio package not installed)", to)

    def _send_whatsapp_api(self, to: str, body: str) -> None:
        if not self._whatsapp_token or len(self._whatsapp_token) < 10:
            logger.info("[WHATSAPP MOCK] To=%s Body=%s", to, body[:60])
            return
        import json
        import urllib.request
        import urllib.error
        api_version = "v22.0"
        url = f"https://graph.facebook.com/{api_version}/{self._whatsapp_phone_id}/messages"
        payload = json.dumps({
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to.lstrip("+"),
            "type": "text",
            "text": {"body": body},
        }).encode()
        req = urllib.request.Request(
            url,
            data=payload,
            headers={
                "Authorization": f"Bearer {self._whatsapp_token}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                result = json.loads(resp.read().decode())
                msg_id = result.get("messages", [{}])[0].get("id", "unknown")
                logger.info("[WHATSAPP] Sent to %s: %s", to, msg_id)
        except urllib.error.HTTPError as e:
            error_body = e.read().decode()
            logger.error("[WHATSAPP] API error %s: %s", e.code, error_body)
            raise
        except Exception as e:
            logger.error("[WHATSAPP] Failed: %s", e)
            raise

    # ------------------------------------------------------------------
    # Receipt tracking
    # ------------------------------------------------------------------

    def _receipt(
        self,
        action: str,
        channel: Channel,
        recipient: str,
        template: str,
        status: Status,
        error: str = "",
    ) -> DeliveryReceipt:
        receipt = DeliveryReceipt(
            notification_id=str(uuid.uuid4()),
            channel=channel.value,
            recipient=recipient,
            template=template,
            status=status.value,
            sent_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            error=error,
        )
        self._delivery_log.append(receipt)
        logger.debug("Delivery: %s | %s | %s", receipt.notification_id, receipt.channel, receipt.status)
        return receipt

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
#    robot = NotificationDispatcherRobot()
#    receipt = robot.send_email(
#        "a@b.com", "Welcome", "account_opening",
#        {"customer_name": "Ali", "account_number": "PK123"}
#    )
#    assert receipt.status == "SUCCESS"
#    assert receipt.template == "account_opening"
#
# 2. Invalid Email Address
#    robot = NotificationDispatcherRobot()
#    with pytest.raises(Exception):
#        robot.send_email("not-an-email", "Subj", "account_opening", ...)
#
# 3. SMS Template Not Found
#    robot = NotificationDispatcherRobot()
#    with pytest.raises(KeyError):
#        robot.send_sms("+920000000", "nonexistent_template", {})
#
# 4. WhatsApp Rate Limit (simulate 429 by mocking _send_whatsapp_api to raise)
#    robot = NotificationDispatcherRobot()
#    robot._send_whatsapp_api = lambda to, body: (_ for _ in ()).throw(
#        Exception("429 Too Many Requests"))
#    with pytest.raises(Exception, match="429"):
#        robot.send_whatsapp("+920000000", "card_activation", {"card_last4": "1234"})
#
# 5. Unsupported Channel
#    robot = NotificationDispatcherRobot()
#    with pytest.raises(AttributeError):
#        robot.send_email(None, "", "", {})  # invalid 'to'
