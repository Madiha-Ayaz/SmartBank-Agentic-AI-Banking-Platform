from __future__ import annotations

import logging

from backend.celery_app import celery_app

logger = logging.getLogger("smartbank.tasks")


@celery_app.task(bind=True, max_retries=3, default_retry_delay=10)
def process_document_background(
    self, file_path: str, customer_id: str  # noqa: ANN201
):
    from document_ai.pipeline import DocumentAIPipeline

    pipeline = DocumentAIPipeline()
    result = pipeline.process_document(file_path, customer_id)
    return {
        "processing_id": result.processing_id,
        "status": result.overall_status,
        "risk_score": result.fraud.risk_score if result.fraud else None,
    }


@celery_app.task(bind=True, max_retries=3, default_retry_delay=5)
def send_notification_background(
    self, channel: str, to: str, template: str, params: dict  # noqa: ANN201
):
    from robots.notification_dispatcher.robot import NotificationDispatcherRobot

    bot = NotificationDispatcherRobot()
    if channel == "email":
        bot.send_email(to, template, params)
    elif channel == "sms":
        bot.send_sms(to, template, params)
    elif channel == "whatsapp":
        bot.send_whatsapp(to, template, params)
    return {"channel": channel, "to": to, "template": template, "status": "sent"}


@celery_app.task
def refresh_dashboard_cache() -> dict:  # noqa: ANN201
    from backend.database import SessionLocal
    from backend.models import Case

    db = SessionLocal()
    try:
        total = db.query(Case).count()
        resolved = db.query(Case).filter(Case.status == "Resolved").count()
        return {"total_cases": total, "resolved": resolved}
    finally:
        db.close()
