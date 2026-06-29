# CBS Connector Robot

## Purpose

Authenticates and transacts with the SmartBank Core Banking System (CBS) — simulating Finacle / Temenos REST API calls. Provides a secure, auditable gateway for all account-level operations.

## Workflow Diagram (UiPath Sequence Flowchart)

```
[Start] → [Get Credentials from Windows Credential Store]
        → [Invoke HTTP POST /login]
        → [Deserialize Token]
        → [Loop: for each account]
            → [Invoke HTTP GET /accounts/{id}]
            → [Invoke HTTP PUT /accounts/{id} (if update needed)]
        → [Invoke HTTP POST /logout]
        → [Write Audit Entry via Queue]
        → [End]
```

## Activity List

| Activity Name | Package | Configuration | Error Handler |
|---|---|---|---|
| Get Robot Credential | UiPath.Credentials | Windows Credential Store | TerminateOnError |
| Invoke HTTP Request - POST /login | UiPath.WebAPI | URL: ${CBS_ENDPOINT}/login | Retry(3, ExpBackoff) |
| Deserialize JSON Response | UiPath.WebAPI | Response → TokenDTO | TerminateOnError |
| Invoke HTTP Request - GET /account | UiPath.WebAPI | URL: ${CBS_ENDPOINT}/accounts/{id} | Retry(3, ExpBackoff) |
| Invoke HTTP Request - PUT /account | UiPath.WebAPI | URL: ${CBS_ENDPOINT}/accounts/{id} | Retry(3, ExpBackoff) |
| Invoke HTTP Request - POST /logout | UiPath.WebAPI | URL: ${CBS_ENDPOINT}/logout | Ignore |
| Write Audit Entry | AuditLogger Robot | Invoke via Queue | TerminateOnError |
| Log Message | UiPath.System.Activities | Level: Info | Ignore |

## Credential Management

- **Windows Credential Store** — robot retrieves CBS_USERNAME and CBS_PASSWORD at runtime via `UiPath.Credentials` Get Robot Credential activity.
- **UiPath Orchestrator Assets** — fallback store; asset names: `CBS.Endpoint`, `CBS.SimulationMode`, `CBS.MockDataPath`.
- No secrets in code, config files, or environment dumps.

## Error Handling Strategy

1. **Retry with exponential backoff** — all HTTP calls (max 3 attempts, backoff: 1s / 2s / 4s).
2. **Token expiry detection** — automatic refresh triggered on 401 response; if refresh fails, session is terminated.
3. **TerminateOnError** — credential failures and serialisation errors stop the workflow immediately.
4. **Ignore** — logout failure is non-fatal; session is cleared in-memory anyway.
5. All exceptions are captured and written to the audit log before propagation.

## Unit Test Scenarios (5)

| # | Scenario | Expected Outcome |
|---|---|---|
| 1 | Happy Path — login → lookup → update → logout | 4 audit entries, all SUCCESS |
| 2 | Invalid Credentials — wrong password | PermissionError raised, last audit = FAILURE |
| 3 | Account Not Found — GET returns fallback mock | Account returned with default fields |
| 4 | Token Expired — force expiry then call GET | Auto-refresh succeeds, account data returned |
| 5 | CBS Timeout — unreachable endpoint | ConnectionError after 3 retries |

## Performance Targets

| Metric | Target |
|---|---|
| Average execution time (per request) | < 500 ms |
| Throughput (transactions/minute) | > 120 |
| Memory ceiling | < 256 MB |
| Token refresh overhead | < 200 ms |
