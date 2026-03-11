# CAM-2026-03-09-QUEUE-RETRY-SEMANTICS-V1

## Goal

Make queue/worker execution semantics explicit and predictable:

- queue-driven retry
- explicit retryable vs terminal failures
- explicit worker shell transport behavior
- status store vocabulary aligned with retry semantics

## Scope

- `src/worker/model.py`
- `src/worker/dispatcher.py`
- `src/worker/worker.py`
- `src/worker/status_store.py`
- `src/entrypoints/queue/worker_shell.py`
- related docs/tests

## Non-goals

- no new command types
- no queue topology rewrite
- no app-level requeue loop

## Implementation skeleton reference

- Primary source: current owner-approved plan in chat
- Trust level: high after verification against active runtime files
- Touchpoints:
  - `src/worker/*`
  - `src/entrypoints/queue/worker_shell.py`
  - `src/entrypoints/http/info_handler.py`
- Forbidden shortcuts:
  - collapsing all failures into generic `failed`
  - hiding retryable failures behind HTTP `200` transport success

## Phases

1. Result/status vocabulary update
2. Dispatcher retryability rules
3. Worker retry/terminal handling
4. Worker shell transport policy
5. Docs/tests/evidence

## DoD

- retryable vs terminal failures are explicit in result and status models
- unknown command and malformed payload are terminal
- transient failures are retryable
- worker shell transport behavior matches queue-driven retry policy
- `/info` can distinguish retryable and terminal failures
