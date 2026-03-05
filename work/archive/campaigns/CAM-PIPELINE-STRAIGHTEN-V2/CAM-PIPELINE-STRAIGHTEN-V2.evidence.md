# CAM-PIPELINE-STRAIGHTEN-V2 Evidence

## Trust Gate
- source: `main.py`, `src/entrypoints/jobs/planner_pipeline_job.py`, `src/services/pipeline_runtime.py`, `src/services/sync_service.py`
- last_verified_at: 2026-03-04
- verified_by: codex
- evidence: code scan + runtime grep before decomposition
- trust_level: high
- notes: previous V1 straightening was completed; V2 starts with re-validation and closure of residual drift only.

## Execution Log
- 2026-03-04: campaign activated.
- 2026-03-04: runtime usage map confirmed by grep.
  - `src/services/pipeline_runtime.py` imports `from src.services.sync_service import YdbSyncService`.
  - no source file `src/services/sync/sync_service.py` exists.
- 2026-03-04: canonical marker added in `src/services/sync_service.py` docstring.
- 2026-03-04: legacy namespace marker updated in `src/services/sync/__init__.py` with `DEPRECATED - DO NOT USE`.
- 2026-03-04: standard timer path rechecked: no `MIGRATION_ENABLE_SOURCE_HASH_GATE`, no state-file hash gate in `main.py`/runtime jobs.
- 2026-03-04: preflight cheap-path verified in `src/services/pipeline_runtime.py`:
  - unchanged preflight -> `full_snapshot_fetch=skipped`
  - changed/stale path -> `full_snapshot_fetch=performed`
- 2026-03-04: local smoke/tests passed.
  - `python -m unittest tests.services.test_pipeline_runtime -v` (4/4 OK)
  - `python -m unittest tests.services.test_sync_source_hash_gate -v` (8/8 OK)
  - `python -m unittest tests.api.test_frontend_api_routing tests.api.test_frontend_api_v2_payload -v` (19/19 OK)
- 2026-03-05: legacy-safe API snapshot recovery path stabilized without touching working legacy timer.
  - `src/services/timer_pipeline.py`: `mode=sync-only` now executes canonical YDB sync/readmodel rebuild even when `store_mode=legacy`.
  - `agent/invoke_function_smoke.py`: added `--force-refresh` payload flag.
  - `scripts/invoke_cloud_timer.cmd`: added `--sync-only` and `--force-refresh` flags (`timer dry-run mock` remains default).
  - docs aligned: `docs/system/entrypoints_index_main.md`, `docs/system/runbook.md`.
- 2026-03-05: fixed runtime crashes caused by legacy integer timestamps in YDB state/readmodel rows.
  - `src/services/sync_service.py`: normalize `last_full_sync_at_utc` (`int|float|str|datetime -> datetime`) before preflight stale-check and state writes.
  - `src/services/timer_pipeline.py`: normalize readmodel `generated_at_utc` before TTL check.
  - Added regressions:
    - `tests/services/test_sync_source_hash_gate.py::test_sync_preflight_handles_legacy_int_last_full_timestamp`
    - `tests/services/test_pipeline_runtime.py::test_pipeline_handles_legacy_int_generated_at_without_crash`
  - Local verification run: `main(mode='sync-only', force_refresh=True)` completed, `migration_readmodel_build ... tasks_count=12`.
