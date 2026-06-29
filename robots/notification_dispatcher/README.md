# Notification Dispatcher Robot

## Purpose

Dispatches multi-channel outbound notifications (Email, SMS, WhatsApp) using 8 Urdu/English templates — one per request type. Tracks delivery status for every message.

## Workflow Diagram (UiPath Sequence Flowchart)

```
[Start] → [Dequeue Notification Request]
        → [Select Channel: Email / SMS / WhatsApp]
        → [Render Template (placeholder substitution)]
        → [Dispatch via Channel]
            → Email:   SMTP (UiPath.Mail.Activities)
            → SMS:     Twilio (UiPath.Twilio.Activities)
            → WhatsApp: WhatsApp Business API (UiPath.WhatsApp.Activities)
        → [Record Delivery Receipt]
        → [Write Audit Entry via Queue]
        → [End]
```

## Activity List

| Activity Name | Package | Configuration | Error Handler |
|---|---|---|---|
| Get Queue Item (Notification) | UiPath.Queue | Queue: NotificationDispatcher | TerminateOnError |
| Send SMTP Email | UiPath.Mail.Activities | SMTP Config: ${SMTP_*} | Retry(3, ExpBackoff) |
| Send SMS (Twilio) | UiPath.Twilio.Activities | Account SID: ${TWILIO_SID} | Retry(3, ExpBackoff) |
| Send WhatsApp Message | UiPath.WhatsApp.Activities | Business API: ${WHATSAPP_TOKEN} | Retry(3, ExpBackoff) |
| Write Delivery Status | UiPath.System.Activities | Status: Sent / Failed | TerminateOnError |
| Write Audit Entry | AuditLogger Robot | Invoke via Queue | TerminateOnError |
| Log Message | UiPath.System.Activities | Level: Info | Ignore |

## Credential Management

- **SMTP credentials** — stored as UiPath Orchestrator Assets (`SMTP.User`, `SMTP.Pass`).
- **Twilio Account SID / Auth Token** — stored in Windows Credential Store, retrieved via `Get Robot Credential`.
- **WhatsApp API Token** — Orchestrator Asset (`WhatsApp.ApiToken`), rotated every 30 days.
- All credentials are injected at runtime; never hardcoded.

## Error Handling Strategy

1. **Retry(3, ExpBackoff)** — each transport channel retries up to 3 times with exponential backoff.
2. **Template not found** — raises `KeyError` immediately (fail-fast).
3. **Invalid recipient** — transport layer rejects; error is captured in DeliveryReceipt.
4. **Rate limiting** — simulated 429 responses are caught and retried; production would integrate with Twilio/WhatsApp rate-limit headers.
5. All outcomes (success and failure) are persisted to the delivery log and audit log.

## Unit Test Scenarios (5)

| # | Scenario | Expected Outcome |
|---|---|---|
| 1 | Happy Path — email sent with correct template | DeliveryReceipt = SUCCESS |
| 2 | Invalid Email Address | Exception raised, receipt = FAILURE |
| 3 | SMS Template Not Found | KeyError raised |
| 4 | WhatsApp Rate Limit (simulated 429) | Exception raised after retries |
| 5 | Unsupported Channel | AttributeError / ValueError raised |

## Performance Targets

| Metric | Target |
|---|---|
| Average execution time (per notification) | < 1 second |
| Throughput (notifications/minute) | > 60 |
| Memory ceiling | < 256 MB |
| Delivery receipt latency | < 100 ms |
