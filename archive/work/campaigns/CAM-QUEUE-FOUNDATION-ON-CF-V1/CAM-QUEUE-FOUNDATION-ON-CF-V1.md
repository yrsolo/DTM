# CAM-QUEUE-FOUNDATION-ON-CF-V1

## Goal

Introduce a command queue foundation for heavy and mutating actions while staying on Yandex Cloud Functions.

## Scope

- command DTO and serializer
- Yandex Message Queue adapter
- queue-triggered worker contour
- S3 JSON job status store
- admin enqueue endpoints and job status lookup
- cron trigger enqueue flow

## Non-goals

- no Serverless Containers
- no Telegram runtime rollout in this CAM
- no file attachments in this CAM
- no permanent worker dependence on `mode=*` orchestration

## Implementation Skeleton Reference

- Primary implementation skeleton: `docs/system/command_queue_skeleton.md`
- Current trust level: medium-high after verification against live runtime files
- Current runtime touchpoints:
  - `index.py`
  - `src/entrypoints/runtime/planner_runtime_entry.py`
  - `src/entrypoints/http/info_handler.py`
  - `src/services/timer_pipeline.py`
- Forbidden shortcuts:
  - Serverless Containers
  - attachments in v1
  - Telegram runtime wiring in v1
  - direct admin heavy execution

## Phases

1. Trust gate and runtime freeze
2. Command model and serialization
3. Queue adapter
4. Worker dispatcher and status store
5. HTTP enqueue/status endpoints
6. Trigger enqueue migration
7. Docs and smoke evidence

## DoD

- heavy admin actions can enqueue commands instead of running inline
- worker can process queue-trigger events in Cloud Functions
- status of queued jobs is visible through S3-backed status lookup
- `/api/v2/*` remains direct snapshot-backed read path
