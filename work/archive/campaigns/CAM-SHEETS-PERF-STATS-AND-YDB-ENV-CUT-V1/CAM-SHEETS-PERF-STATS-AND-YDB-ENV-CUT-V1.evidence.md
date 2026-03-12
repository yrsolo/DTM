# CAM-SHEETS-PERF-STATS-AND-YDB-ENV-CUT-V1 Evidence

## Trust gate
- source: active runtime code and focused tests
- last_verified_at: 2026-03-11
- verified_by: Codex
- trust_level: high

## Verified implementation
- `SheetSnapshot` carries `status_colors`
- `SheetsNormalizedTaskSource.read_snapshot()` reads worksheet values and canonical `A`-column colors only
- `SheetsNormalizedTaskSource.build_tasks_from_snapshot()` performs no Google API calls
- active snapshot runtime path uses direct row builders instead of DataFrame-heavy repository conversion
- Grafana spec derives `last` via `last_over_time(...)` and `avg5` via panel transformations over raw metrics
- active deploy workflows no longer inject `YDB_*` secrets
- loader allowlist no longer accepts `YDB_*`
- bootstrap/runtime no longer exposes YDB endpoint/database deps

## Evidence
- focused tests:
  - `tests.services.test_sheets_normalized_source`
  - `tests.api.test_info_observability`
  - `tests.infra.test_grafana_specs`
  - `tests.snapshot_engine.test_update_job`
  - `tests.snapshot_engine.test_update_job_timings`
  - `tests.api.test_runtime_execution`
  - `tests.services.test_pipeline_runtime`
- guards:
  - `scripts/check_no_legacy_entrypoint_imports.py`
  - `scripts/check_no_legacy_imports.py`
- grep of active tree shows no remaining YDB deploy/runtime contour except:
  - archived docs
  - YDB adapter/tests
  - agent-only migration/backfill utilities with local explicit endpoint/database resolution

## Notes
- live `test` verification of lower `fetch_sheet_ms` / `normalize_ms` and populated stat panels is still required after rollout
- runtime-derived `*_last_ms` / `*_last5_avg_ms` gauges were intentionally removed in favor of dashboard-side aggregation
- YDB adapter code remains in repo as non-active/agent-only legacy surface
