# CAM-2026-03-09-QUEUE-RETRY-SEMANTICS-V1 Evidence

## Trust gate

- source: active runtime code
- last_verified_at: 2026-03-09
- verified_by: Codex
- evidence:
  - `src/worker/model.py`
  - `src/worker/dispatcher.py`
  - `src/worker/worker.py`
  - `src/entrypoints/queue/worker_shell.py`
  - `src/worker/status_store.py`
- trust_level: high
- notes: active queue foundation existed, but retry semantics were incomplete before this CAM

## Delivered

- `JobResult` now carries `retryable`, `failure_kind`, `error_code`
- status store now writes `accepted`, `running`, `success`, `failed_retryable`, `failed_terminal`
- worker distinguishes malformed payload, unknown command, transient failures, and terminal failures
- worker shell now returns non-success transport only when retry is requested

## Proof

- `tests/worker/test_retry_semantics.py`
- `tests/worker/test_status_store_history.py`
- `tests/api/test_worker_shell.py`
- `tests/api/test_command_queue_foundation.py`
