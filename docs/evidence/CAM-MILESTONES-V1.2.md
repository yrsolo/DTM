# CAM-MILESTONES-V1.2 Evidence

## Fixed risks
- `R1`: legacy milestones hot write is disabled by default (`WRITE_LEGACY_MILESTONES=0`).
- `R2`: readmodel builder guarantees non-empty milestones using synthetic `start`.
- `R3`: version bump path reordered and guarded against missing milestones_v/current_version drift.

## New flag
- `WRITE_LEGACY_MILESTONES=0|1` (default `0`)
  - `0` -> skip `dtm_task_milestones` updates in sync hot path.
  - `1` -> keep compat writes for migration/debug only.

## Validation commands
- `.venv\Scripts\python.exe -m tests.services.test_sync_source_hash_gate`
- `.venv\Scripts\python.exe -m tests.services.test_readmodel_uses_milestones_table`
- `.venv\Scripts\python.exe -m tests.adapters.test_ydb_operational_repo_milestones_bulk`
- `.venv\Scripts\python.exe -m tests.api.test_frontend_api_routing`

## Expected logs
- `legacy_milestones_write=skipped reason=disabled`
- `milestones_synthetic_start_count=<N>`
- `milestones_write_empty` (negative test / forced stub path)

## Cloud smoke result
- `.venv\Scripts\python.exe agent/cloud_smoke_db_migration_v2.py --base-url https://functions.yandexcloud.net/<test-id> --api-url https://<API_DOMAIN_TEST>/api/v2/frontend --timeout 90`
- Output:
  - `sync_status_code=200`
  - `api_status_code=200`
  - `api_contract_version=2.0.1`
  - `api_tasks_count=11`
  - `api_ok=true`
