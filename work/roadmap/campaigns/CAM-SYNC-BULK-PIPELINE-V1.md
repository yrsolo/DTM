# CAM-SYNC-BULK-PIPELINE-V1

## Goal
Remove N+1 YDB writes in sync runtime path and switch version/archive persistence to bulk batches.

## Scope
- Add repo bulk methods for task versions upsert/archive.
- Refactor sync service to accumulate version/archive rows in memory and flush in bulk.
- Keep revision/version semantics unchanged.
- Add tests for bulk adapter and runtime guard against single-row calls.

## Out of scope
- API contract changes.
- Color parsing cleanup.
- Legacy timer functional redesign.

## DoD
- No per-task `upsert_task_version` / `archive_task_version` calls in sync runtime loop.
- Sync result/logs expose bulk counters for versions and milestones_v.
- Target tests are green.
