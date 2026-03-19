# Command Runtime Architecture

## Current topology

The current runtime uses one Cloud Function object per environment:

- the same deployed function handles HTTP gateway events
- the same deployed function also handles Message Queue trigger events

This is important: current docs must not describe a separate dedicated worker function unless topology is intentionally changed later.

## Read path (sync)

Read-only HTTP paths stay synchronous:

- `/api/*`
- `/info`
- admin/status reads

Read sources:

- Snapshot Engine / prep snapshot
- job status store
- live Yandex queue/function metadata for operator visibility

## Command intake path (async)

The following paths validate, build internal `Command`, enqueue, and return quickly:

- admin enqueue endpoints
- attachment metadata enqueue after presigned upload-contract issuance
- telegram webhook
- trigger shell when queue mode is enabled
- hidden admin trigger-emulation endpoint for operator/debug intake parity

These paths must not execute heavy business logic inline.

Current trigger fan-out:

- `timer` trigger enqueues a batch of three commands:
  - `update_snapshot`
  - `render_timeline_sheet`
  - `render_designers_sheet`
- `morning` trigger enqueues one `send_reminders` command

Queue caveat:

- current queue type is `Standard`, so enqueue order is preserved in the shell response but strict cross-message execution ordering is not guaranteed by the queue itself

## Worker path

Message Queue trigger -> worker shell -> worker -> dispatcher -> one job

Worker responsibilities:

1. deserialize command
2. write `running`
3. dispatch to one job wrapper
4. write terminal status
5. follow queue retry policy

## Active command types

- `update_snapshot`
- `send_reminders`
- `render_timeline_sheet`
- `render_designers_sheet`
- `group_query_reply`
- `attach_task_file`

Attachment upload contract:
- `POST /ops/admin/task-attachments/request-upload` returns a presigned upload contract after task-exists validation
- binary upload happens directly against Object Storage
- `POST /ops/admin/task-attachments/finalize` verifies the object and enqueues `attach_task_file`
- `POST /ops/admin/task-attachments/delete` enqueues `delete_task_attachment`
- legacy paths remain as transitional wrappers only

## Status and observability

Operator truth sources:

- job status store for recent execution truth
- `/info` for operational dashboard
- structured logs for bounded event traces
- metrics abstraction for counters/timings
- Yandex Monitoring custom metrics backend when enabled

## Runtime boundaries

Thin top-level shell:

- `index.py`
- `src/entrypoints/index_dispatcher.py`

Transport shells:

- `src/entrypoints/http/http_shell.py`
- `src/entrypoints/queue/worker_shell.py`
- `src/entrypoints/triggers/trigger_shell.py`
- `src/entrypoints/runtime/runtime_shell.py`

Local/manual runtime still passes through a transitional runtime adapter, but that adapter is not the conceptual center of the current architecture.

Historical runtime detail is archive-only:
- `src/archive/legacy_runtime/`
- `docs/archive/system_legacy/modules/*`
