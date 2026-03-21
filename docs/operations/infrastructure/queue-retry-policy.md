# Queue Retry Policy

## Scope

This policy defines how queue-driven command execution behaves in the current runtime:

- intake endpoints enqueue internal commands
- Yandex Message Queue delivers command messages
- the same Cloud Function runtime handles MQ trigger events
- worker and dispatcher decide whether a failure is retryable or terminal

## Selected model

- Retry model: `queue_driven`
- App-level requeue loop: `disabled`
- Batch policy: `per_message`
- Worker shell transport result:
  - `200` when all processed messages finished with `success` or `failed_terminal`
  - `503` when at least one processed message finished with `failed_retryable`

This keeps terminal failures visible in status/history without asking the queue to retry them forever, while still allowing transient failures to be retried by queue/trigger mechanics.

## Failure classes

### Success

- job completed successfully
- message may be acknowledged/removed by the trigger
- job status: `success`

### Retryable failure

- temporary external failure
- retry may help without changing payload or code
- examples:
  - transient Sheets/API timeout
  - temporary Object Storage/network issue
  - rate limit / quota exhaustion

Worker result:
- `success = false`
- `retryable = true`
- `failure_kind = "retryable"`

Job status:
- `failed_retryable`

Transport behavior:
- worker shell returns non-success transport (`503`) so queue/trigger may retry according to queue visibility / receive-count policy

### Terminal failure

- retry will not help without changing payload or code
- examples:
  - malformed command payload
  - unsupported command type
  - business validation failure
  - impossible task reference

Worker result:
- `success = false`
- `retryable = false`
- `failure_kind = "terminal"`

Job status:
- `failed_terminal`

Transport behavior:
- worker shell still returns `200`
- the message is not retried by transport
- investigation happens through recent job history and `/info`

## Duplicate handling

If the same `job_id` is observed again:

- existing `success` -> idempotent duplicate, soft skip
- existing `running` -> duplicate-in-flight, soft skip

This is not treated as failure.

## Unknown and malformed commands

- unknown command type -> `failed_terminal`
- malformed JSON / invalid command payload -> `failed_terminal`

These cases must never be silently ignored.

## DLQ notes

Current queue setup must remain aligned with this policy:

- main queue retries retryable failures
- poison messages should eventually end in DLQ after queue-level max receive count
- worker does not auto-consume DLQ

Operational visibility:

- `/info` shows recent retryable vs terminal failures from job status history
- queue live depth is visible via `queue.live`

## Source of truth

- worker result model: `src/platform/runtime/worker/model.py`
- worker semantics: `src/platform/runtime/worker/worker.py`
- status store: `src/platform/runtime/worker/status_store.py`
- worker transport shell: `src/entrypoints/queue/worker_shell.py`
