# CAM-HISTORY-FIELD-NORMALIZATION-V1 Evidence

## Trust Gate
- source: code (`src/adapters/ydb/schema.py`, `src/adapters/ydb/operational_repo.py`, `src/services/readmodel_builder.py`, `src/entrypoints/http/frontend_v2_handler.py`) + runtime artifacts from recent local/cloud checks in current thread.
- last_verified_at: 2026-03-05
- verified_by: codex
- evidence:
  - runtime API used stale readmodel snapshot before explicit rebuild,
  - local timer updates sheet correctly,
  - `history` observed in API contract but previously materialized through raw payload path.
- trust_level: high
- notes: hard-cutover accepted by owner; destructive reset for TEST is explicitly allowed.

## Completed Tasks
- [x] CAM-HISTORY-FIELD-NORMALIZATION-V1-P01-T001
- [x] CAM-HISTORY-FIELD-NORMALIZATION-V1-P02-T001
- [x] CAM-HISTORY-FIELD-NORMALIZATION-V1-P03-T001
- [x] CAM-HISTORY-FIELD-NORMALIZATION-V1-P04-T001
- [x] CAM-HISTORY-FIELD-NORMALIZATION-V1-P05-T001
- [x] CAM-HISTORY-FIELD-NORMALIZATION-V1-P06-T001

## Verification
- Unit/contract tests:
  - `python -m unittest tests.adapters.test_ydb_schema_history_column -v`
  - `python -m unittest tests.adapters.test_ydb_operational_repo_history -v`
  - `python -m unittest tests.services.test_readmodel_uses_milestones_table -v`
  - `python -m unittest tests.services.test_sync_source_hash_gate tests.services.test_task_payloads_job tests.api.test_frontend_api_v2_payload tests.api.test_frontend_api_routing -v`
  - `python scripts/check_no_monsters.py`
- TEST DB reset + rebuild:
  - Drop+recreate operational/readmodel tables in `ENV=test` via `YdbClient` + `ensure_tables`.
  - Cloud invoke attempt: `scripts\\invoke_cloud_timer.cmd --sync-only --force-refresh --live` (HTTP 200 body `!GOOD!`, but no readmodel row).
  - Deterministic rebuild from local contour against same TEST YDB: `ENV=test .venv\\Scripts\\python.exe local_run.py --mode sync-only`.
- Post-rebuild checks:
  - API: `/api/v2/frontend?statuses=work,pre_done&include_people=true&limit=200` -> `tasksReturned=12`, `tasksTotal=12`, `queryFilterApplied=true`, `readmodelSource=ydb`.
  - YDB counts after rebuild:
    - `dtm_tasks_total=1028`
    - `dtm_tasks_non_empty_history=937`
    - `dtm_tasks_active=12`

## Notes
- Hard cutover applied:
  - `history` column added to schema + alter migration hook.
  - Operational write/read path uses `dtm_tasks.history`.
  - Readmodel/API `history` extraction from `raw_payload` removed.
- Residual operational quirk:
  - Cloud function currently can return `!GOOD!` even when sync/readmodel step is deferred (error swallowed in timer pipeline); local sync-only was used to complete rebuild reliably.
