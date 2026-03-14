# Entrypoints Behavior (Current)

This document describes only the active entrypoint/runtime boundary.

## Top-level runtime entry

`index.py` is the canonical top-level cloud entrypoint.

Responsibilities:
- accept event/context
- lazily resolve runtime context
- delegate to dispatcher
- avoid business logic and import-time side effects

`index.py` must stay:
- thin
- import-safe
- transport-oriented

## Dispatcher and transport shells

Active routing lives in:
- `src/entrypoints/index_dispatcher.py`
- `src/entrypoints/event_classifier.py`

Transport shells:
- `src/entrypoints/http/http_shell.py`
- `src/entrypoints/queue/worker_shell.py`
- `src/entrypoints/triggers/trigger_shell.py`
- `src/entrypoints/runtime/runtime_shell.py`

## HTTP boundary

Current HTTP handlers:
- `FrontendRootHandler`
- `FrontendV2Handler`
- `PeopleSnapshotHandler`
- `TelegramWebhookHandler`
- `GroupQueryHandler`
- `AdminQueueHandler`
- `InfoHandler`

Browser auth note:
- `/ops/auth/*` and `/test/ops/auth/*` are external auth-contour routes, not Python handlers in this repo
- this runtime receives browser data requests under `/ops/api/*` and `/test/ops/api/*`
- trusted browser auth state enters only through validated proxy headers at the access boundary

## API source of truth

For API v2 runtime:
- canonical source: prep snapshot in Object Storage
- handler path: `src/entrypoints/http/frontend_v2_handler.py`
- query engine: `src/snapshot_engine/query_engine.py`

Current payload policy:
- one canonical frontend payload shape
- masking is post-build transform only
- read path is read-only and side-effect free

## Trigger and worker behavior

Trigger policy:
- trigger shell is intake/fan-out only
- queue-backed trigger execution is the default mutation path

Current trigger fan-out:
- `timer` enqueues:
  - `update_snapshot`
  - `render_timeline_sheet`
  - `render_designers_sheet`
- `morning` enqueues:
  - `send_reminders`

Worker policy:
- one queue message -> one internal command -> one job execution path
- retry semantics follow `docs/system/queue_retry_policy.md`

## Local/manual runtime

Local/manual runtime helpers live under:
- `local_run.py`
- `src/entrypoints/runtime/local_runtime.py`
- `src/entrypoints/runtime/runtime_shell.py`

There is still a transitional runtime adapter involved in that path, but it is not the conceptual center of the current architecture.

## Archive pointer

Historical planner-era entrypoint stories and deeper legacy runtime detail are archive-only.
If needed, use:
- `docs/archive/system_legacy/modules/*`
- `src/legacy/*`
