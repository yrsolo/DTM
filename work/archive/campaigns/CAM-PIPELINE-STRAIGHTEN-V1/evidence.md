# CAM-PIPELINE-STRAIGHTEN-V1 Evidence

## Trust Registry
| source | last_verified_at | verified_by | evidence | trust_level | notes |
|---|---|---|---|---|---|
| `main.py`, `src/entrypoints/jobs/planner_pipeline_job.py`, `src/entrypoints/jobs/hash_gate_job.py`, `src/services/pipeline_runtime.py`, `src/services/sync_service.py` | 2026-03-04 | TeamLead agent | direct code scan (`rg` + file reads) | high | confirms old gate still existed in runtime path at campaign start and full snapshot read was unconditional |
| `tests/services/test_planner_pipeline_job.py`, `tests/services/test_sync_source_hash_gate.py`, `tests/services/test_pipeline_runtime.py` | 2026-03-04 | TeamLead agent | direct test contour scan | high | identifies minimum smoke contour for straightening changes |

## Execution Log
- `STRAIGHTEN-P01-T001` completed: trust-gate verified against runtime code and tests before decomposition.
- `STRAIGHTEN-P02-T001` completed: removed old main hash-gate coupling from runtime wiring (`main.py`, `planner_pipeline_job.py`) and aligned unit test for planner pipeline helper.
- `STRAIGHTEN-P03-T001` completed: implemented preflight-driven skip in pipeline runtime (`run_preflight_only` + conditional full snapshot fetch).
- `STRAIGHTEN-P04-T001` completed: updated `docs/system/dataflow.md` to single canonical gate semantics and added tests for skip/performed full-snapshot paths.
- `STRAIGHTEN-P02-T002` completed: removed dead old-gate artifacts from active contour (`src/entrypoints/jobs/hash_gate_job.py`, `src/services/sync/hash_basis.py`, `src/services/sync/hash_gate.py`, unused constants/tests).

## Verification
- `rg -n "MIGRATION_ENABLE_SOURCE_HASH_GATE|build_hash_basis|evaluate_hash_gate|save_last_hash|run_ydb_sync_readmodel_pipeline|src\\.services\\.sync_service|src\\.services\\.sync\\.sync_service" src main.py tests`
- `python -m unittest tests.services.test_planner_pipeline_job tests.services.test_sync_source_hash_gate tests.api.test_frontend_api_routing -v`
- `python -m unittest tests.services.test_pipeline_runtime tests.services.test_planner_pipeline_job tests.services.test_sync_source_hash_gate tests.api.test_frontend_api_routing -v`
- `rg -n "MIGRATION_ENABLE_SOURCE_HASH_GATE|MIGRATION_HASH_GATE_STATE_FILE|resolve_allow_sync_by_hash_gate|hash_gate_job|services\\.sync\\.hash_gate|services\\.sync\\.hash_basis" src main.py index.py tests config`
