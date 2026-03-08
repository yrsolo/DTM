# CAM-ADMIN-ACTIONS-ASYNC-V1

## Goal

Move `/info` admin actions from synchronous execution to enqueue plus status-tracked UX.

## Scope

- convert admin buttons to enqueue requests
- show queued/running/succeeded/failed job state
- keep info page snapshot diagnostics read-only and synchronous

## Non-goals

- no redesign of `/info`
- no direct worker topology changes outside queue foundation

## Implementation Skeleton Reference

- Primary implementation skeleton: `docs/system/command_queue_skeleton.md`
- Current trust level: medium-high
- Current touchpoints:
  - `src/entrypoints/http/info_handler.py`
  - `src/entrypoints/http/router.py`
  - `index.py`
- Depends on: `CAM-QUEUE-FOUNDATION-ON-CF-V1`
- Forbidden shortcuts:
  - no blind `HTTP 200` without job state
  - no fallback to sync heavy execution from admin buttons

## Phases

1. Admin enqueue endpoints
2. Job status endpoint
3. `/info` UI migration
4. Smoke verification

## DoD

- `/info` buttons enqueue work instead of performing heavy actions inline
- `/info` shows real job state and latest outcomes
- sync read-only info block remains fast
