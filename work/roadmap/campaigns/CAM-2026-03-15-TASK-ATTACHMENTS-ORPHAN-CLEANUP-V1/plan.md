# CAM-2026-03-15-TASK-ATTACHMENTS-ORPHAN-CLEANUP-V1

## Goal
Add minimal operational cleanup for stale attachment records that never became `ready` or were already logically deleted.

## Target behavior
- stale `pending_upload` older than 24h -> delete object best-effort, remove metadata
- stale `uploaded_unverified` older than 24h -> delete object best-effort, remove metadata
- stale `deleted` older than 24h -> best-effort physical delete, then remove stale metadata
- `ready` records are never touched
- `delete_pending` younger than TTL is never touched

## Implementation shape
- add internal command type `cleanup_task_attachments`
- add one cleanup job
- add one hidden operator enqueue endpoint first
- reuse bulk extra snapshot as the physical metadata carrier
- rebuild prep at most once per cleanup run if changes were made

## Acceptance
- stale records are removed correctly
- transient storage failures are downgraded to warnings
- rerun is idempotent
- cleanup is safe on empty or partially malformed metadata snapshots

## Notes
- TTL for v1: 24h
- no preview/summary cleanup in this wave
