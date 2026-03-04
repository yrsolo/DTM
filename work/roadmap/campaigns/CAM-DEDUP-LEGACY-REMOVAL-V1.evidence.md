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
- `DEDUP-P02-T002` completed: removed unused duplicate `src/services/sync/sync_service.py`; `src/services/sync/__init__.py` now exports only hash primitives.
- `DEDUP-P02-T003` completed: removed legacy build-readmodels branch (`src/handlers/build_readmodels.py`, `src/services/readmodels/*`) and related tests.
- `DEDUP-P02-T004` completed: removed legacy placeholder `src/handlers/api.py`; docs aligned to `src/entrypoints/http/*` as active API boundary.
- `DEDUP-P02-T005` completed: removed legacy placeholder handler stubs `src/handlers/render_sheets.py` and `src/handlers/notify_morning.py`; docs aligned.
- `DEDUP-P02-T006` completed: removed empty legacy package marker `src/handlers/__init__.py`; verified no active imports of `src.handlers` namespace.
- `DEDUP-P02-T007` completed: synced `docs/system/module_map.md` to reflect finished sync/handler dedup wave (removed stale conflict note).
- `DEDUP-P02-T008` completed: removed unused legacy frontend payload serializer `core/api_payload.py`; docs synced to v2 payload-only active contour.

## Verification
- `rg -n "from src\\.services\\.sync_service|from src\\.services\\.sync\\.sync_service|from src\\.services\\.readmodels\\.builder|from src\\.services\\.readmodel_builder" src main.py index.py tests`
- `rg -n "from src\\.handlers\\.sync|from src\\.handlers\\.build_readmodels" src main.py index.py tests`
- `rg -n "src\\.handlers\\.sync|handle_sync\\(" src tests`
- `python -m unittest tests.handlers.test_build_readmodels_handler tests.services.test_planner_pipeline_job tests.api.test_frontend_api_routing -v`
- `rg -n "from src\\.services\\.sync\\.sync_service|SyncService\\(" src tests`
- `python -m unittest tests.services.test_hash_gate_job tests.services.test_sync_source_hash_gate tests.services.test_planner_pipeline_job tests.api.test_frontend_api_routing -v`
- `rg -n "src\\.handlers\\.build_readmodels|src\\.services\\.readmodels|build_read_models\\(|publish_read_model_to_file\\(" src tests main.py index.py`
- `python -m unittest tests.services.test_planner_pipeline_job tests.services.test_sync_source_hash_gate tests.api.test_frontend_api_routing -v`
- `rg -n "src\\.handlers\\.api|handle_api\\(" src tests main.py index.py docs/system`
- `python -m unittest tests.services.test_planner_pipeline_job tests.services.test_sync_source_hash_gate tests.api.test_frontend_api_routing -v`
- `rg -n "src\\.handlers\\.(render_sheets|notify_morning)|from src\\.handlers import (render_sheets|notify_morning)|handle_render_sheets|handle_notify_morning" src tests main.py index.py docs work`
- `python -m unittest tests.services.test_planner_pipeline_job tests.services.test_sync_source_hash_gate tests.api.test_frontend_api_routing -v`
- `rg -n "from src\\.handlers|import src\\.handlers|src\\.handlers" src tests main.py index.py docs work`
- `python -m unittest tests.services.test_planner_pipeline_job tests.api.test_frontend_api_routing -v`
- manual doc consistency pass:
  - `docs/system/module_map.md`
  - `docs/system/dedup_plan.md`
- `rg -n "core\\.api_payload\\b|from core\\.api_payload import|build_frontend_api_payload\\(" src tests main.py index.py`
- `python -m unittest tests.api.test_frontend_api_routing -v`
- manual read pass:
  - `src/services/sync_service.py`
  - `src/services/sync/sync_service.py`
  - `src/services/readmodel_builder.py`
  - `src/services/readmodels/builder.py`
