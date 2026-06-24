"""
SmartFinance AI — Communication Agent

Generates personalized, contextual messages for customer communications
based on the problem type, resolution action, and customer profile.

Technology: UiPath Agent Builder, LLM Agent
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional

logger = logging.getLogger("smartbank.agents.communication")


@dataclass
class CommunicationMessage:
    problem_type: str
    subject: str
    body: str
    sms_text: str
    push_text: str
    whatsapp_text: str
    tone: str
    urgency: str
    timestamp: str


class AICommunicationAgent:
    MESSAGE_TEMPLATES = {
        "FRAUD": {
            "subject": "Fraud Alert - SmartFinance AI Has Protected Your Account",
            "body": (
                "Dear {customer_name},\n\n"
                "Our AI Guardian detected unusual activity on your account. "
                "We have temporarily blocked the suspicious transaction to protect your funds.\n\n"
                "Transaction Details:\n"
                "- Amount: Rs.{amount}\n"
                "- Location: {location}\n"
                "- Time: {timestamp}\n\n"
                "If this was you, please reply APPROVE to unblock.\n"
                "If this wasn't you, no action needed — we've secured your account.\n\n"
                "Your security is our priority.\n- SmartFinance AI Guardian"
            ),
            "sms": "ALERT: Unusual transaction of Rs.{amount} detected at {location}. Your account is protected. Reply APPROVE if this was you.",
            "push": "Fraud alert! Rs.{amount} transaction at {location} blocked. Tap to review.",
            "whatsapp": "🚨 *Fraud Alert*\n\nYour account is protected! Unusual Rs.{amount} transaction blocked at {location}.\n\nReply *APPROVE* if this was you.",
            "tone": "urgent",
            "urgency": "HIGH",
        },
        "BILL": {
            "subject": "Bill Payment Reminder - SmartFinance AI Guardian Alert",
            "body": (
                "Dear {customer_name},\n\n"
                "Your {biller} bill of Rs.{amount} is due on {due_date}. "
                "Your current balance is Rs.{balance}, which may be insufficient.\n\n"
                "Recommended Actions:\n"
                "- Deposit funds before {due_date}\n"
                "- Schedule a partial payment\n"
                "- Apply for overdraft protection\n\n"
                "We're here to help you avoid late fees.\n- SmartFinance AI Guardian"
            ),
            "sms": "Reminder: {biller} bill of Rs.{amount} due {due_date}. Balance: Rs.{balance}. Pay now to avoid late fees.",
            "push": "Bill alert: {biller} payment of Rs.{amount} due soon. Balance is low.",
            "whatsapp": "📅 *Bill Reminder*\n\nYour *{biller}* bill of *Rs.{amount}* is due on *{due_date}*.\n\nCurrent balance: *Rs.{balance}*\n\nTap to view payment options.",
            "tone": "informative",
            "urgency": "MEDIUM",
        },
        "RECOVERY": {
            "subject": "Refund Initiated - SmartFinance AI Recovered Your Money",
            "body": (
                "Dear {customer_name},\n\n"
                "We detected a failed transaction where Rs.{amount} was deducted at {merchant}. "
                "Our AI Recovery Agent has automatically initiated a refund.\n\n"
                "Refund Details:\n"
                "- Amount: Rs.{amount}\n"
                "- Merchant: {merchant}\n"
                "- Refund Reference: {refund_ref}\n"
                "- Expected Credit: 3-5 business days\n\n"
                "No action needed from your side.\n- SmartFinance AI Guardian"
            ),
            "sms": "Refund of Rs.{amount} from {merchant} initiated. Ref: {refund_ref}. Credit in 3-5 days.",
            "push": "Refund of Rs.{amount} from {merchant} initiated. Tap for details.",
            "whatsapp": "✅ *Refund Initiated*\n\nWe recovered *Rs.{amount}* from *{merchant}*.\n\nReference: {refund_ref}\nExpected: 3-5 business days.",
            "tone": "reassuring",
            "urgency": "MEDIUM",
        },
        "COACH": {
            "subject": "Your Monthly Financial Health Report - SmartFinance AI Coach",
            "body": (
                "Dear {customer_name},\n\n"
                "Here's your personalized financial health summary:\n\n"
                "Health Score: {health_score}/100\n"
                "Spending Trend: {spending_trend}\n"
                "Potential Monthly Savings: Rs.{savings_potential}\n\n"
                "Top Recommendations:\n"
                "{recommendations}\n\n"
                "Small changes can make a big difference.\n- SmartFinance AI Coach"
            ),
            "sms": "Your financial health score: {health_score}/100. You can save Rs.{savings_potential}/month. Check the app for details.",
            "push": "Financial health score: {health_score}. Save Rs.{savings_potential} monthly!",
            "whatsapp": "📊 *Financial Health Update*\n\nScore: *{health_score}/100*\nSavings potential: *Rs.{savings_potential}/month*\n\nTap for personalized recommendations.",
            "tone": "encouraging",
            "urgency": "LOW",
        },
        "RESOLVED": {
            "subject": "Issue Resolved - SmartFinance AI Guardian",
            "body": (
                "Dear {customer_name},\n\n"
                "Your issue has been resolved successfully.\n\n"
                "Summary:\n"
                "- Problem: {problem_type}\n"
                "- Resolution: {resolution_action}\n"
                "- Reference: {case_id}\n"
                "- Resolution Time: {resolution_time}\n\n"
                "We resolved this proactively before it could inconvenience you.\n"
                "- SmartFinance AI Guardian"
            ),
            "sms": "Issue resolved! Ref: {case_id}. {problem_type} handled proactively. Thank you for banking with SmartFinance.",
            "push": "Issue resolved! {problem_type} handled proactively by AI Guardian.",
            "whatsapp": "✅ *Issue Resolved*\n\nType: {problem_type}\nReference: {case_id}\n\nResolved proactively by SmartFinance AI Guardian.",
            "tone": "positive",
            "urgency": "LOW",
        },
    }

    def __init__(self, config: Optional[dict[str, Any]] = None):
        self.config = config or {}
        self.llm_api_key = self.config.get("llm_api_key", "")

    def generate_message(
        self,
        problem_type: str,
        customer_name: str,
        params: dict[str, Any],
    ) -> CommunicationMessage:
        template = self.MESSAGE_TEMPLATES.get(problem_type, self.MESSAGE_TEMPLATES["RESOLVED"])

        formatted_params = {
            "customer_name": customer_name,
            "case_id": params.get("case_id", "N/A"),
            "amount": params.get("amount", "N/A"),
            "merchant": params.get("merchant", "N/A"),
            "location": params.get("location", "N/A"),
            "timestamp": params.get("timestamp", "N/A"),
            "due_date": params.get("due_date", "N/A"),
            "biller": params.get("biller", "N/A"),
            "balance": params.get("balance", "N/A"),
            "refund_ref": params.get("refund_ref", "N/A"),
            "health_score": params.get("health_score", "N/A"),
            "savings_potential": params.get("savings_potential", "N/A"),
            "spending_trend": params.get("spending_trend", "stable"),
            "recommendations": params.get("recommendations", ""),
            "resolution_action": params.get("resolution_action", "N/A"),
            "resolution_time": params.get("resolution_time", "N/A"),
            "problem_type": problem_type,
        }

        return CommunicationMessage(
            problem_type=problem_type,
            subject=template["subject"].format(**formatted_params),
            body=template["body"].format(**formatted_params),
            sms_text=template["sms"].format(**formatted_params),
            push_text=template["push"].format(**formatted_params),
            whatsapp_text=template["whatsapp"].format(**formatted_params),
            tone=template["tone"],
            urgency=template["urgency"],
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
