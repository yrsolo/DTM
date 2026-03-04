# CAM-DEDUP-LEGACY-REMOVAL-V1 Evidence

## Trust Registry
| source | last_verified_at | verified_by | evidence | trust_level | notes |
|---|---|---|---|---|---|
| `main.py`, `index.py`, `src/services/pipeline_runtime.py` | 2026-03-04 | TeamLead agent | direct runtime import scan | high | confirms active runtime contour for dedup decisions |
| `src/services/sync_service.py`, `src/services/sync/sync_service.py`, `src/services/readmodel_builder.py`, `src/services/readmodels/*`, `src/handlers/*` | 2026-03-04 | TeamLead agent | duplicate-role inventory via `rg` + direct file reads | high | duplicate implementations identified with keep/remove candidates |

## Execution Log
- `DEDUP-P01-T001` completed: duplicate-role inventory prepared for sync/readmodel/handler branches.
- `DEDUP-P01-T002` completed: keep/remove decisions documented in `docs/system/dedup_plan.md`.
- `DEDUP-P02-T001` completed: removed legacy runtime-unused `src/handlers/sync.py` and `tests/handlers/test_sync_handler.py`.

## Verification
- `rg -n "from src\\.services\\.sync_service|from src\\.services\\.sync\\.sync_service|from src\\.services\\.readmodels\\.builder|from src\\.services\\.readmodel_builder" src main.py index.py tests`
- `rg -n "from src\\.handlers\\.sync|from src\\.handlers\\.build_readmodels" src main.py index.py tests`
- `rg -n "src\\.handlers\\.sync|handle_sync\\(" src tests`
- `python -m unittest tests.handlers.test_build_readmodels_handler tests.services.test_planner_pipeline_job tests.api.test_frontend_api_routing -v`
- manual read pass:
  - `src/services/sync_service.py`
  - `src/services/sync/sync_service.py`
  - `src/services/readmodel_builder.py`
  - `src/services/readmodels/builder.py`
