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
- telegram webhook
- trigger shell when queue mode is enabled

These paths must not execute heavy business logic inline.

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

Standard runtime entry:

- `src/entrypoints/runtime/planner_runtime_entry.py`

Legacy runtime code is archived under `src/legacy/` and is not part of standard runtime.
