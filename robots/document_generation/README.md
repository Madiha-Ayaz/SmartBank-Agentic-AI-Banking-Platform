# Document Generation Robot

## Purpose

Generates branded PDF documents — account statements, customer letters, and confirmations for all 8 request types. Supports Urdu + English text, local file storage, and simulated digital signing.

## Workflow Diagram (UiPath Sequence Flowchart)

```
[Start] → [Dequeue Document Request]
        → [Select Template by Request Type]
        → [Render PDF (fpdf2)]
            → [Embed Urdu font if available]
            → [Populate placeholders]
        → [Write PDF to {OUTPUT_DIR}/{doc_id}.pdf]
        → [Simulate Digital Signature → {doc_id}.pdf.sig]
        → [Write Audit Entry via Queue]
        → [End]
```

## Activity List

| Activity Name | Package | Configuration | Error Handler |
|---|---|---|---|
| Get Queue Item (Document Request) | UiPath.Queue | Queue: DocumentGeneration | TerminateOnError |
| Build PDF - Statement | UiPath.PDF.Activities | Template: Statement | Retry(2) |
| Build PDF - Activation Letter | UiPath.PDF.Activities | Template: ActivationLetter | Retry(2) |
| Build PDF - Confirmation | UiPath.PDF.Activities | Template: Confirmation | Retry(2) |
| Sign PDF | UiPath.PDF.Activities | Certificate: SmartBankRootCA | TerminateOnError |
| Store PDF to Filesystem | UiPath.System.Activities | Path: ${OUTPUT_DIR}/{doc_id}.pdf | TerminateOnError |
| Write Audit Entry | AuditLogger Robot | Invoke via Queue | TerminateOnError |
| Log Message | UiPath.System.Activities | Level: Info | Ignore |

## Credential Management

- **No secrets required** for document generation itself.
- **Digital signature certificate** — stored in Windows Certificate Store; accessed via UiPath.PDF.Activities Sign PDF activity.
- **Output path** — configured via Orchestrator asset `DOCUMENT_OUTPUT_DIR`.

## Error Handling Strategy

1. **Retry(2)** — PDF rendering retried once on failure (e.g. font loading issue).
2. **TerminateOnError** — disk write failures and queue deserialisation errors halt the workflow.
3. **Validation gate** — empty account IDs and unsupported letter types raise `ValueError` before any PDF work begins.
4. All errors are captured in the audit log.

## Unit Test Scenarios (5)

| # | Scenario | Expected Outcome |
|---|---|---|
| 1 | Happy Path — statement generated | PDF file exists on disk, checksum is 64 hex chars |
| 2 | Unsupported Letter Type | ValueError raised |
| 3 | Empty Account ID | ValueError raised |
| 4 | Urdu Text Rendering | PDF binary contains expected English fallback |
| 5 | Output File Missing (non-writable dir) | PermissionError raised |

## Performance Targets

| Metric | Target |
|---|---|
| Average execution time (per document) | < 2 seconds |
| Throughput (documents/minute) | > 30 |
| Memory ceiling | < 512 MB |
| PDF file size (typical) | < 200 KB |
