# CAM-2026-03-22-JOB-STATUS-RETENTION-CLEANUP-V1 Evidence

## Trust Gate

- source: current local code on `dev` plus live object-storage inspection
- last_verified_at: 2026-03-22
- verified_by: Codex
- evidence:
  - `src/platform/runtime/worker/status_store.py`
  - `src/platform/runtime/orchestration.py`
  - `src/entrypoints/triggers/trigger_shell.py`
  - `src/entrypoints/http/admin_queue_handler.py`
  - `aws --endpoint-url https://storage.yandexcloud.net s3 ls s3://dtm/`
- trust_level: high
- notes: active bucket growth is dominated by `jobs/*/status/*.json`; this wave targets only that operational residue and leaves `history/*` plus `latest/*` intact.

## Outcome

- added platform command `cleanup_job_statuses`,
- made `morning` enqueue cleanup first and reminders second in best-effort batch mode,
- added safe pruning of old terminal `jobs/{env}/status/{job_id}.json` records,
- added manual admin enqueue route for exact cutoff or relative retention,
- documented that `status/{job_id}.json` is short-lived while `latest/*` and `history/*` remain.

## Checks

- `python -m unittest tests.platform.runtime.worker.test_status_store_history tests.platform.runtime.test_job_status_cleanup_job tests.platform.test_orchestration tests.entrypoints.http.test_command_queue_foundation tests.architecture.test_guardrails_v0 tests.entrypoints.test_import_safety -v`
- `python scripts/check_no_monsters.py`
- `python scripts/check_entrypoint_import_boundaries.py`
- `python scripts/check_active_import_boundaries.py`
