# CAM-2026-03-22-JOB-STATUS-RETENTION-CLEANUP-V1

## Goal

Add a platform-owned cleanup command for old terminal job-status records and wire it into the `morning` trigger as one independent morning event.

## Scope

1. Add `cleanup_job_statuses` to the runtime command taxonomy and queue bootstrap.
2. Make `morning` enqueue cleanup plus reminders in best-effort batch mode.
3. Add safe status-store pruning, admin enqueue support, tests, and active docs/runbook updates.

## Non-goals

- no deletion of `history/*` or `latest/*`,
- no retention changes for attachments or snapshots,
- no reminder-module ownership changes.
