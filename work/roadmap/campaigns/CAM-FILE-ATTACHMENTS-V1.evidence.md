# Evidence - CAM-FILE-ATTACHMENTS-V1

## Trust Gate

- source:
  - `src/snapshot_engine/model.py`
  - `src/snapshot_engine/prep_builder.py`
  - `src/snapshot_engine/stores/s3_store.py`
- last_verified_at: 2026-03-08
- verified_by: codex
- trust_level: high
- evidence:
  - Snapshot engine already has extra-store contour suitable for metadata extension.
  - No attachment metadata model is present yet.
  - Queue foundation is live in code and test env, so attachment mutation can be implemented as a worker-side command.
  - `src/entrypoints/http/admin_queue_handler.py`, `src/worker/dispatcher.py`, and `src/jobs/update_snapshot_job.py` already show the established command -> worker -> S3 status pattern.

## Notes

- Depends on `CAM-QUEUE-FOUNDATION-ON-CF-V1`.
- Primary implementation source doc: `docs/system/file_attachments_skeleton.md`
- implementation_result_2026-03-08:
  - `TaskExtra` now stores first-class `attachments[]` metadata in snapshot extra-store.
  - hidden admin endpoint `POST /admin/attachments/request-upload` returns direct Object Storage upload contract for an existing task.
  - queue command `attach_task_file` updates extra-store and rebuilds prep from current raw snapshot without moving binary through queue/runtime.
  - API v2 exposes attachment metadata via `tasks[].attachments` while hiding internal storage keys.
- tests_verified:
  - `python -m unittest tests.snapshot_engine.test_s3_store -v`
  - `python -m unittest tests.snapshot_engine.test_prep_builder -v`
  - `python -m unittest tests.snapshot_engine.test_query_engine -v`
  - `python -m unittest tests.jobs.test_attach_task_file_job -v`
  - `python -m unittest tests.api.test_command_queue_foundation -v`
