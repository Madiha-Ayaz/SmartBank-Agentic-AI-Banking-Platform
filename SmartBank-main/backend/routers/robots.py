from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException, Request

from backend.auth import get_current_user

logger = logging.getLogger("smartbank.routers.robots")
router = APIRouter(prefix="/api/robots", tags=["Robots"])


@router.get("/status")
def robot_status(current_user=Depends(get_current_user)) -> dict:
    return {
        "robots": [
            {"name": "CBS Connector", "status": "Online", "mode": "Simulation"},
            {"name": "Document Generation", "status": "Online", "mode": "Active"},
            {"name": "Notification Dispatcher", "status": "Online", "mode": "Active"},
            {"name": "Audit Logger", "status": "Online", "mode": "Immutable"},
            {"name": "Transaction Processing Bot", "status": "Online", "mode": "Simulation"},
            {"name": "Communication Bot", "status": "Online", "mode": "Simulation"},
            {"name": "Reporting Bot", "status": "Online", "mode": "Simulation"},
        ]
    }


@router.post("/notification/send")
async def robot_send_notification(
    request: Request,
    current_user=Depends(get_current_user),
) -> dict:
    body = await request.json()
    from robots.notification_dispatcher.robot import NotificationDispatcherRobot
    bot = NotificationDispatcherRobot()
    channel = body.get("channel", "email")
    to = body.get("to", "")
    template = body.get("template", "card_activation")
    params = body.get("params", {})
    success = False
    if channel == "email":
        success = bot.send_email(to, template, params)
    elif channel == "sms":
        success = bot.send_sms(to, template, params)
    elif channel == "whatsapp":
        success = bot.send_whatsapp(to, template, params)
    else:
        raise HTTPException(status_code=400, detail=f"Unknown channel: {channel}")
    return {"success": success, "channel": channel}


@router.post("/document/generate")
async def robot_generate_document(
    request: Request,
    current_user=Depends(get_current_user),
) -> dict:
    body = await request.json()
    from robots.document_generation.robot import DocumentGenerationRobot
    bot = DocumentGenerationRobot()
    doc_type = body.get("type", "statement")
    params = body.get("params", {})
    if doc_type == "statement":
        path = bot.generate_statement(
            params.get("account_id", "ACC-001"),
            params.get("from", ""),
            params.get("to", ""),
        )
    elif doc_type == "letter":
        path = bot.generate_letter(
            params.get("letter_type", "account_opening"),
            params.get("customer_name", "Customer"),
        )
    elif doc_type == "confirmation":
        path = bot.generate_confirmation(
            params.get("request_type", "card_activation"),
            params.get("customer_name", "Customer"),
        )
    else:
        raise HTTPException(status_code=400, detail=f"Unknown type: {doc_type}")
    return {"path": str(path), "type": doc_type}


@router.get("/audit/verify")
def robot_audit_verify(current_user=Depends(get_current_user)) -> dict:
    from robots.audit_logger.robot import AuditLoggerRobot
    bot = AuditLoggerRobot()
    valid = bot.verify_integrity()
    return {"integrity_valid": valid}
