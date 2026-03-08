# Command Queue Skeleton

## Purpose

Source of truth for future command queue implementation on top of Yandex Cloud Functions.

This document defines the target module layout, contracts, boundaries, and migration path for queued execution of heavy or mutating actions.

## Goal

Introduce one explicit command contour for heavy and mutating operations so that:
- read APIs stay synchronous and snapshot-backed,
- admin actions enqueue jobs instead of executing them inline,
- scheduled triggers enqueue work,
- worker logic is isolated from HTTP request handling.

## Non-goals

- No Serverless Container rollout.
- No file attachments in queue foundation v1.
- No Telegram webhook runtime integration in queue foundation v1.
- No permanent dependence on `mode=*` switch orchestration as worker API.

## Chosen Infra

- Queue provider: `Yandex Message Queue` standard queue
- Worker target: one deployed `Cloud Function` object handling queue trigger events
- Job status store: `S3 JSON` in Object Storage
- Read source: `SnapshotEngine`

## Event Routing

Top-level routing must distinguish exactly:

1. HTTP gateway event
2. Message Queue trigger event
3. healthcheck event
4. unsupported event shape

Unsupported event shapes must fail closed with structured diagnostics and must not fall through into planner runtime modes.

## Module Tree

### Commands
- `src/commands/model.py`
- `src/commands/types.py`
- `src/commands/serializer.py`
- `src/commands/queue.py`
- `src/commands/yandex_mq.py`

### Worker
- `src/worker/model.py`
- `src/worker/dispatcher.py`
- `src/worker/worker.py`
- `src/worker/status_store.py`

### Jobs
- `src/jobs/update_snapshot_job.py`
- `src/jobs/send_reminders_job.py`
- `src/jobs/render_timeline_job.py`
- `src/jobs/render_designers_job.py`

### HTTP handlers
- `src/entrypoints/http/admin_queue_handler.py`
- `src/entrypoints/http/job_status_handler.py`

## Public Contracts

## Command

Required fields:
- `job_id`
- `type`
- `created_at_utc`
- `requested_by`
- `payload`
- `idempotency_key`

`requested_by` fields:
- `source`
- `user_id`
- `chat_id`

Supported command types for v1:
- `update_snapshot`
- `send_reminders`
- `render_timeline_sheet`
- `render_designers_sheet`

Future command types are intentionally excluded from queue foundation v1.
They are specified in separate skeleton docs and separate CAM files.

## Job Status Record

Required fields:
- `job_id`
- `command_type`
- `status`
- `requested_at_utc`
- `started_at_utc`
- `finished_at_utc`
- `requested_by`
- `summary`
- `warnings`
- `error`

Allowed status values:
- `queued`
- `running`
- `succeeded`
- `failed`

## S3 Layout

Status keys:
- `jobs/{env}/status/{job_id}.json`
- `jobs/{env}/latest/{command_type}.json`

Queue foundation must not introduce YDB-backed job status tracking.

## Per-module Contracts

## `src/commands/model.py`
- Owns DTOs only.
- No cloud SDK imports.
- No snapshot or business logic imports.

## `src/commands/types.py`
- Owns command type constants and validation registry.
- No runtime wiring.

## `src/commands/serializer.py`
- Converts `Command <-> JSON`.
- Must validate required fields.
- Must use deterministic key ordering and ISO datetime encoding.

## `src/commands/queue.py`
- Defines producer/consumer abstractions and message envelope.
- No Yandex SDK specifics.

## `src/commands/yandex_mq.py`
- Owns Yandex MQ specifics.
- Must parse queue-trigger events into queue message envelopes.
- Must not contain business dispatch logic.

## `src/worker/model.py`
- Owns `JobResult` and `JobStatusRecord`.
- No cloud SDK imports.

## `src/worker/dispatcher.py`
- Dispatches supported command types to one job wrapper each.
- Must not import `index.py`.
- Must not directly parse HTTP or queue event shapes.

## `src/worker/worker.py`
- Handles one queue-trigger event batch.
- Reads messages, deserializes commands, updates status store, calls dispatcher.
- No polling loop required for cloud trigger runtime.

## `src/worker/status_store.py`
- Owns S3 job status persistence.
- Must be environment-scoped.
- Must not depend on YDB.

## Job wrappers
- Must call extracted service/job entrypoints.
- Must not keep permanent dependence on `planner_runtime_entry.py` mode strings.
- May temporarily wrap existing runtime jobs during migration, but target is direct use-case orchestration.

## HTTP handlers
- `admin_queue_handler`: enqueue only, no heavy execution
- `job_status_handler`: read-only status lookup
- Both must remain thin and use `AppContext`

## Current Touchpoints To Replace Or Extend

- [index.py](n:/PROJECTS/python/SCRIPT/DTM/index.py)
- [src/entrypoints/runtime/planner_runtime_entry.py](n:/PROJECTS/python/SCRIPT/DTM/src/entrypoints/runtime/planner_runtime_entry.py)
- [src/entrypoints/http/info_handler.py](n:/PROJECTS/python/SCRIPT/DTM/src/entrypoints/http/info_handler.py)
- [src/services/timer_pipeline.py](n:/PROJECTS/python/SCRIPT/DTM/src/services/timer_pipeline.py)
- [src/notify/job.py](n:/PROJECTS/python/SCRIPT/DTM/src/notify/job.py)
- [src/render/job.py](n:/PROJECTS/python/SCRIPT/DTM/src/render/job.py)

## Migration Path

1. Add command DTO, serializer, queue adapter, status store
2. Add worker dispatcher and wrappers over existing snapshot/reminder/render jobs
3. Add enqueue/status HTTP handlers
4. Move `/info` buttons to enqueue flow
5. Move cron triggers to enqueue flow
6. Keep old direct runtime modes temporarily as debug-only path
7. Later remove heavy synchronous admin execution after queue path is stable

## Forbidden Shortcuts

- No Serverless Containers
- No attachments in v1
- No Telegram runtime wiring in v1
- No worker path that permanently calls monolithic `mode=*` orchestration
- No status tracking in YDB
- No direct heavy execution from admin HTTP actions after async admin CAM starts
