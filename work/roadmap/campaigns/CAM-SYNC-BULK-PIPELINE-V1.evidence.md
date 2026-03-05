# CAM-SYNC-BULK-PIPELINE-V1 Evidence

## Trust Gate
- source: runtime code (`src/services/sync_service.py`, `src/adapters/ydb/operational_repo.py`, `src/services/timer_pipeline.py`) + tests
- last_verified_at: 2026-03-05
- verified_by: codex
- evidence:
  - runtime previously called single-row version writes inside task loop
  - adapter had no bulk version/archive methods
  - targeted tests reproduced pipeline behavior and validated fixes
- trust_level: high
- notes: assertions in test stub now fail if legacy single-row calls are used in runtime path

## Implemented
- Added `upsert_task_versions_bulk(rows)` in `OperationalTaskRepo` with chunking.
- Added `archive_task_versions_bulk(rows)` in `OperationalTaskRepo` with chunking.
- Refactored `YdbSyncService.run()` to accumulate `versions_rows_bulk` and `archives_rows_bulk` and flush once.
- Added `SyncRunResult` counters:
  - `version_rows_upserted`
  - `version_rows_archived`
  - `milestones_v_rows_upserted`
- Extended `TimerPipeline` operational log with new counters (backward-safe via `getattr`).
- Added tests:
  - `tests/adapters/test_ydb_operational_repo_versions_bulk.py`
  - `tests/services/test_sync_source_hash_gate.py::test_run_path_does_not_use_single_row_version_methods`

## Test Runs
- `python -m unittest tests.services.test_sync_source_hash_gate -v` -> OK
- `python -m unittest tests.adapters.test_ydb_operational_repo_versions_bulk -v` -> OK
- `python -m unittest tests.services.test_pipeline_runtime -v` -> OK

## Remaining
- Optional live smoke (`sync-only --force-refresh`) to measure real `ydb_queries_count` drop in cloud logs.
