# Entrypoints Behavior (Current)

This document describes only the active entrypoint/runtime boundary.

## Top-level runtime entry

`index.py` is the canonical top-level cloud entrypoint.

Responsibilities:
- accept event/context
- lazily resolve runtime context
- delegate to the canonical entrypoint handler
- avoid business logic and import-time side effects

`index.py` must stay:
- thin
- import-safe
- transport-oriented

Current active top path:
- `index.py`
- `src/entrypoint/handler.py`
- `src/platform/bootstrap.py` lazy shell getters
- `src/entrypoints/http/http_shell.py` or `src/entrypoints/queue/worker_shell.py` or `src/entrypoints/triggers/trigger_shell.py`

## Dispatcher and transport shells

Active routing lives in:
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
- `AdminTaskAttachmentsHandler`
- `TaskAttachmentReadHandler`
- `AdminQueueHandler`
- `InfoHandler`

Admin attachment note:
- canonical attachment admin routes live in `AdminTaskAttachmentsHandler`:
  - `POST /ops/admin/task-attachments/request-upload`
  - `POST /ops/admin/task-attachments/finalize`
  - `POST /ops/admin/task-attachments/delete`
  - same routes under `/test`
- browser-safe attachment reads live in `TaskAttachmentReadHandler`:
  - `GET /ops/api/task-attachments/{attachment_id}/view`
  - `GET /ops/api/task-attachments/{attachment_id}/download`
- binary upload goes directly to Object Storage; metadata attach/delete goes through the queue
- legacy paths remain supported ingress aliases:
  - `POST /admin/attachments/request-upload`
  - `POST /admin/commands/attach-task-file`

Browser auth note:
- `/ops/auth/*` and `/test/ops/auth/*` are external auth-contour routes, not Python handlers in this repo
- this runtime receives browser data requests under `/ops/api/*` and `/test/ops/api/*`
- trusted browser auth state enters only through validated proxy headers at the access boundary

## API source of truth

For API v2 runtime:
- canonical source: prep snapshot in Object Storage
- handler path: `src/contexts/access_api/internal/frontend_v2_handler.py` via `src/entrypoints/http/router.py`
- query engine: `src/contexts/snapshot/internal/engine/query_engine.py`

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
- retry semantics follow `docs/operations/infrastructure/queue-retry-policy.md`

## Local/manual runtime

Local/manual runtime helpers live under:
- `local_run.py`
- `src/entrypoints/runtime/local_runtime.py`
- `src/entrypoints/runtime/runtime_shell.py`

Local/manual runtime uses the same canonical runtime shell family and is not a separate architectural center.

## Archive pointer

Historical planner-era entrypoint stories and deeper legacy runtime detail are archive-only.
If needed, use:
- `docs/archive/system_legacy/modules/*`
- `src/archive/legacy_runtime/*`
