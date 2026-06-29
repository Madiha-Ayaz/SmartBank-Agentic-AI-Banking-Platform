# Audit Logger Robot

## Purpose

Writes immutable, append-only audit entries for every action across all SmartBank robots. Implements a SHA-256 hash chain for tamper-evident integrity and simulates the Elasticsearch index pattern `smartbank-audit-{YYYY.MM}` on the local filesystem.

## Workflow Diagram (UiPath Sequence Flowchart)

```
[Start] → [Receive Queue Item (Audit Entry)]
        → [Read previous entry's hash from log file]
        → [Compute SHA-256(current_payload + previous_hash)]
        → [Append JSON line to audit-{YYYY.MM}.json]
        → [Optional: Verify Integrity (walk last N entries)]
        → [End]
```

## Activity List

| Activity Name | Package | Configuration | Error Handler |
|---|---|---|---|
| Receive Queue Item (Audit Entry) | UiPath.Queue | Queue: AuditLogger | TerminateOnError |
| Compute SHA-256 Hash Chain | UiPath.System.Activities | Input: previous_hash + payload | TerminateOnError |
| Append Entry to JSON Log | UiPath.System.Activities | Path: audit-{YYYY.MM}.json | Retry(2) |
| Verify Integrity (last N entries) | UiPath.System.Activities | Mode: periodic check | TerminateOnError |
| Log Message | UiPath.System.Activities | Level: Info | Ignore |

## Credential Management

- **No credentials required** — the audit logger is a pure logging component.
- **Log directory** — configured via Orchestrator asset `AuditLog.DirectoryPath`.

## Error Handling Strategy

1. **Retry(2)** — file append is retried once on I/O error.
2. **TerminateOnError** — hash computation failure and queue deserialisation errors stop the workflow.
3. **Thread-safe** — a module-level lock ensures concurrent writes do not corrupt the file.
4. **Malformed line handling** — `verify_integrity()` skips corrupted lines with a warning rather than crashing.
5. **Genesis hash** — the first entry's `previous_hash` is 64 zero-characters.

## Unit Test Scenarios (5)

| # | Scenario | Expected Outcome |
|---|---|---|
| 1 | Happy Path — entry written | File exists and contains a valid JSON line |
| 2 | Hash Chain Continuity | entry_2.previous_hash == entry_1.hash |
| 3 | Integrity Check Detects Tamper | verify_integrity() returns False after corruption |
| 4 | Concurrent Append (2 threads) | Both entries written, no data loss |
| 5 | Missing Log Directory | Directory auto-created, write succeeds |

## Performance Targets

| Metric | Target |
|---|---|
| Average execution time (per entry) | < 50 ms |
| Throughput (entries/second) | > 200 |
| Memory ceiling | < 128 MB |
| Monthly log file size (estimate) | < 50 MB (at 100k entries/month) |
