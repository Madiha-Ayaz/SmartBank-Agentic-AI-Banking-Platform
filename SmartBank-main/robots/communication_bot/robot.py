"""
SmartFinance Communication Bot

UiPath RPA — Multi-channel customer communication dispatcher.
Sends SMS, Email, WhatsApp, and mobile app notifications based on
the AI Communication Agent's generated messages.

UiPath Activity Map:
  Activity Name                   | Package                     | Configuration
  --------------------------------|-----------------------------|----------------------------------------
  Get Queue Item (Notification)   | UiPath.Queue                | Queue: CommunicationDispatcher
  Build Message Template          | UiPath.String.Activities    | Template: ${templateName}
  Send SMTP Email                 | UiPath.Mail.Activities      | SMTP Config: ${SMTP_*}
  Send SMS (Twilio)               | UiPath.Twilio.Activities    | Account SID: ${TWILIO_SID}
  Send WhatsApp Message           | UiPath.WhatsApp.Activities  | Business API: ${WHATSAPP_TOKEN}
  Send Push Notification          | UiPath.Mobile.Activities    | FCM: ${FCM_KEY}
  Write Delivery Status           | UiPath.System.Activities    | Status: Sent / Failed
  Log Message                     | UiPath.System.Activities    | Level: Info
"""

from __future__ import annotations

import json
import logging
import uuid
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

logger = logging.getLogger("smartbank.robots.communication")


class Channel(str, Enum):
    SMS = "sms"
    EMAIL = "email"
    WHATSAPP = "whatsapp"
    PUSH = "push"


class DeliveryStatus(str, Enum):
    SENT = "SENT"
    FAILED = "FAILED"
    PENDING = "PENDING"


@dataclass
class CommunicationRequest:
    customer_id: str
    case_id: str
    channel: str
    template: str
    recipient: str
    params: dict[str, Any]
    priority: str = "NORMAL"


@dataclass
class CommunicationResult:
    request_id: str
    channel: str
    status: str
    message: str
    delivery_ref: Optional[str] = None


TEMPLATES = {
    "fraud_alert": {
        "sms": "ALERT: Unusual transaction detected on your account. If this wasn't you, reply BLOCK or call our 24/7 helpline.",
        "email": "Fraud Alert - Unusual Activity Detected\n\nDear {customer_name},\n\nWe detected unusual activity on your account. Amount: Rs.{amount} at {merchant}. If this wasn't you, please contact us immediately.\n\n- SmartFinance AI Guardian",
        "whatsapp": "⚠️ *Fraud Alert*\n\nDear {customer_name},\n\nWe detected an unusual transaction of *Rs.{amount}* at *{merchant}*.\n\nReply *BLOCK* to block your card or contact our helpline.",
        "push": "Fraud Alert: Rs.{amount} transaction at {merchant}. Not you? Tap to block.",
    },
    "bill_reminder": {
        "sms": "Reminder: Your {biller} bill of Rs.{amount} is due in {days} day(s). Current balance may be insufficient.",
        "email": "Bill Payment Reminder\n\nDear {customer_name},\n\nYour {biller} bill of Rs.{amount} is due on {due_date}. Your current balance is Rs.{balance}. Please ensure sufficient funds.\n\n- SmartFinance AI Guardian",
        "whatsapp": "📅 *Bill Reminder*\n\nDear {customer_name},\n\nYour *{biller}* bill of *Rs.{amount}* is due on *{due_date}*.\nCurrent balance: *Rs.{balance}*\n\nTap to pay now.",
        "push": "Bill Reminder: {biller} payment of Rs.{amount} due in {days} day(s)",
    },
    "refund_initiated": {
        "sms": "Good news! Refund of Rs.{amount} from {merchant} has been initiated. Expected in 3-5 business days.",
        "email": "Refund Initiated\n\nDear {customer_name},\n\nYour refund of Rs.{amount} from {merchant} has been initiated. It should reflect in your account within 3-5 business days.\n\n- SmartFinance AI Guardian",
        "whatsapp": "✅ *Refund Initiated*\n\nDear {customer_name},\n\nYour refund of *Rs.{amount}* from *{merchant}* has been initiated.\n\nExpected credit: 3-5 business days.",
        "push": "Refund of Rs.{amount} from {merchant} has been initiated",
    },
    "coach_advice": {
        "sms": "SmartFinance Tip: Your monthly spending increased by {increase_pct}%. Check our app for saving suggestions.",
        "email": "Financial Health Update\n\nDear {customer_name},\n\nYour spending increased by {increase_pct}% this month. Here are personalized recommendations to save Rs.{potential_saving} monthly.\n\n- SmartFinance AI Coach",
        "whatsapp": "💡 *Finance Tip*\n\nDear {customer_name},\n\nYour spending increased by *{increase_pct}%* this month.\n\nWe found ways to save *Rs.{potential_saving}* monthly. Check the app!",
        "push": "Spending up {increase_pct}%. Save Rs.{potential_saving} monthly - tap to see how",
    },
    "resolution_complete": {
        "sms": "Your issue has been resolved! Ref: {case_id}. Thank you for banking with SmartFinance.",
        "email": "Issue Resolved Successfully\n\nDear {customer_name},\n\nYour request (Ref: {case_id}) has been resolved. Our AI Guardian detected and fixed the issue proactively.\n\n- SmartFinance AI Guardian",
        "whatsapp": "✅ *Issue Resolved*\n\nDear {customer_name},\n\nYour issue has been resolved successfully!\n\nReference: {case_id}",
        "push": "Issue resolved! Ref: {case_id}",
    },
}


class CommunicationBot:
    def __init__(self, config: Optional[dict[str, Any]] = None):
        self.config = config or {}
        self.simulation_mode = self.config.get("simulation_mode", True)

    def send(self, request: CommunicationRequest) -> CommunicationResult:
        request_id = str(uuid.uuid4())

        if request.channel not in [c.value for c in Channel]:
            return CommunicationResult(
                request_id=request_id,
                channel=request.channel,
                status=DeliveryStatus.FAILED.value,
                message=f"Unsupported channel: {request.channel}",
            )

        template = TEMPLATES.get(request.template, {}).get(request.channel)
        if not template:
            return CommunicationResult(
                request_id=request_id,
                channel=request.channel,
                status=DeliveryStatus.FAILED.value,
                message=f"Template not found: {request.template}/{request.channel}",
            )

        rendered = self._render_template(template, request.params)
        delivery_ref = None

        if self.simulation_mode:
            delivery_ref = f"DEL-{uuid.uuid4().hex[:8].upper()}"
            logger.info(f"[SIMULATION] {request.channel.upper()} to {request.recipient}: {rendered[:100]}...")
            return CommunicationResult(
                request_id=request_id,
                channel=request.channel,
                status=DeliveryStatus.SENT.value,
                message="Message sent (simulation mode)",
                delivery_ref=delivery_ref,
            )

        try:
            if request.channel == Channel.SMS.value:
                delivery_ref = self._send_sms(request.recipient, rendered)
            elif request.channel == Channel.EMAIL.value:
                delivery_ref = self._send_email(request.recipient, rendered, request.template)
            elif request.channel == Channel.WHATSAPP.value:
                delivery_ref = self._send_whatsapp(request.recipient, rendered)
            elif request.channel == Channel.PUSH.value:
                delivery_ref = self._send_push(request.recipient, rendered)

            return CommunicationResult(
                request_id=request_id,
                channel=request.channel,
                status=DeliveryStatus.SENT.value,
                message="Message sent successfully",
                delivery_ref=delivery_ref,
            )
        except Exception as e:
            logger.error(f"Failed to send {request.channel} message: {e}")
            return CommunicationResult(
                request_id=request_id,
                channel=request.channel,
                status=DeliveryStatus.FAILED.value,
                message=f"Delivery error: {str(e)}",
            )

    def _render_template(self, template: str, params: dict) -> str:
        return template.format(**params)

    def _send_sms(self, to: str, message: str) -> str:
        from robots.notification_dispatcher.robot import NotificationDispatcherRobot
        bot = NotificationDispatcherRobot()
        bot.send_sms(to, message)
        return f"SMS-{uuid.uuid4().hex[:8].upper()}"

    def _send_email(self, to: str, body: str, subject: str) -> str:
        from robots.notification_dispatcher.robot import NotificationDispatcherRobot
        bot = NotificationDispatcherRobot()
        bot.send_email(to, subject, {"message": body})
        return f"EML-{uuid.uuid4().hex[:8].upper()}"

    def _send_whatsapp(self, to: str, message: str) -> str:
        from robots.notification_dispatcher.robot import NotificationDispatcherRobot
        bot = NotificationDispatcherRobot()
        bot.send_whatsapp(to, message)
        return f"WAP-{uuid.uuid4().hex[:8].upper()}"

    def _send_push(self, to: str, message: str) -> str:
        ref = f"PSH-{uuid.uuid4().hex[:8].upper()}"
        logger.info(f"Push notification to {to}: {message}")
        return ref
