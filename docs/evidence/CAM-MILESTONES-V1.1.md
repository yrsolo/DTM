# CAM-MILESTONES-V1.1 Evidence Snapshot

## Scope
- Remove milestone dual-source risk.
- Keep version-safe milestone read/write path.
- Run migration with fallback and verify sampled consistency.

## Runtime Results
- Migration command:
  - `.venv\Scripts\python.exe -m agent.migrate_milestones_to_v --apply`
- Result:
  - `tasks_total=999`
  - `tasks_with_current_version=999`
  - `tasks_from_legacy_table=999`
  - `tasks_from_raw_payload=0`
  - `rows_prepared=5732`
  - `rows_written=5732`
  - `verify_sample_size=10`
  - `verify_matches=10`
  - `verify_mismatches=0`

## Smoke
- `.venv\Scripts\python.exe agent/cloud_smoke_db_migration_v2.py --base-url https://functions.yandexcloud.net/<test-id> --api-url https://<API_DOMAIN_TEST>/api/v2/frontend --timeout 90`
- Result:
  - `sync_status_code=200`
  - `api_status_code=200`
  - `api_contract_version=2.0.1`
  - `api_ok=true`

## Quality Notes
- `replace_task_milestones_bulk` no longer uses full-table delete.
- Readmodel builder keeps version guard for milestones rows (`task_id + current_version`).
