# Evidence - CAM-2026-03-15-TASK-ATTACHMENTS-ORPHAN-CLEANUP-V1

## Trust gate
- source: current attachment metadata store, current snapshot engine, current attachment docs
- last_verified_at: 2026-03-15
- verified_by: Codex
- evidence:
  - `src/services/attachments/metadata_store.py`
  - `src/snapshot_engine/engine.py`
  - `src/services/attachments/storage.py`
  - `docs/system/file_attachments.md`
- trust_level: high
- notes:
  - metadata is stored only in bulk extra snapshot
  - there is currently no orphan cleanup path
  - stale attachment cleanup can be implemented without introducing a new store

## Implementation evidence
- implemented_at: 2026-03-15
- files:
  - `src/commands/types.py`
  - `src/entrypoints/http/admin_queue_handler.py`
  - `src/jobs/cleanup_task_attachments_job.py`
  - `src/worker/dispatcher.py`
  - `src/app/bootstrap.py`
  - `src/snapshot_engine/engine.py`
  - `tests/jobs/test_cleanup_task_attachments_job.py`
  - `tests/snapshot_engine/test_engine_cleanup_attachments.py`
  - `tests/api/test_command_queue_foundation.py`
- behavior:
  - added hidden enqueue path `POST /admin/commands/cleanup-task-attachments`
  - added internal command `cleanup_task_attachments`
  - stale cleanup scans only bulk extra snapshot metadata
  - removes stale `pending_upload`, `uploaded_unverified`, and `deleted` records older than TTL
  - attempts best-effort storage delete before removing metadata
  - keeps record and emits warning when storage delete fails transiently
  - rebuilds prep at most once per cleanup run when metadata changed
- verification:
  - `python -m unittest tests.jobs.test_cleanup_task_attachments_job tests.snapshot_engine.test_engine_cleanup_attachments tests.api.test_command_queue_foundation`
  - result: passed
