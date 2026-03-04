# CAM-ENTRYPOINT-HYGIENE-V1 Evidence

## Trust Registry
| source | last_verified_at | verified_by | evidence | trust_level | notes |
|---|---|---|---|---|---|
| `index.py`, `src/entrypoints/http/http_dispatch_chain.py`, `src/entrypoints/http/runtime_execution.py`, `src/entrypoints/jobs/planner_pipeline_job.py`, `src/services/pipeline_runtime.py` | 2026-03-04 | TeamLead agent | direct code scan (`rg` + file reads) | high | hyperfunction signatures confirmed in active runtime path |
| `tests/api/test_frontend_api_routing.py`, `tests/services/test_pipeline_runtime.py`, `tests/services/test_planner_pipeline_job.py` | 2026-03-04 | TeamLead agent | direct smoke contour scan | high | baseline verification set for hygiene refactors |

## Execution Log
- `HYGIENE-P01-T001` completed: trust-gate baseline captured; identified parameter-sheet hotspots in HTTP dispatch and runtime pipeline functions.
- `HYGIENE-P02-T001` completed: introduced `HttpDispatchHandlersContext` to collapse `build_http_dispatch_handlers(...)` argument sheet into a typed context object; `index.py` wiring switched to context construction.
- `HYGIENE-P02-T002` completed: introduced `RuntimeExecutionContext` and `RuntimeExecutionRequest` for `execute_runtime(...)`; `index.py` runtime call now passes typed context/request instead of keyword argument sheet.
- `HYGIENE-P03-T001` completed: introduced `PlannerPipelineContext` and `PlannerPipelineRequest` for `run_planner_pipeline(...)`; shared runtime entry now passes typed DTOs instead of long keyword lists.
- `HYGIENE-P03-T002` completed: introduced `SyncReadmodelPipelineContext` and `SyncReadmodelPipelineRequest` for `run_ydb_sync_readmodel_pipeline(...)`; planner pipeline now composes and passes typed DTOs.
- `HYGIENE-P03-T003` completed: introduced `GroupQueryHandlerContext` and `GroupQueryHandlerRequest`; `index.py` now passes typed DTOs to `handle_group_query_if_requested(...)`.
- `HYGIENE-P04-T001` completed: final signature audit confirms no parameter sheets in active runtime methods; remaining `**kwargs` wrappers are thin entrypoint compatibility adapters (`main.py`, `run_planner_runtime`).

## Verification
- `rg -n "^def |^async def " src/entrypoints src/services | rg -n "build_http_dispatch_handlers|execute_runtime|run_planner_pipeline|run_ydb_sync_readmodel_pipeline|run_planner_runtime|dispatch_http|handle_group_query_if_requested"`
- `Get-Content src/entrypoints/http/http_dispatch_chain.py`
- `Get-Content src/entrypoints/http/runtime_execution.py`
- `Get-Content src/entrypoints/jobs/planner_pipeline_job.py`
- `Get-Content src/services/pipeline_runtime.py`
- `python -m unittest tests.api.test_frontend_api_routing tests.services.test_pipeline_runtime tests.services.test_planner_pipeline_job -v`
- `Get-Content src/entrypoints/http/runtime_execution.py`
- `python -m unittest tests.api.test_frontend_api_routing tests.services.test_pipeline_runtime tests.services.test_planner_pipeline_job tests.services.test_sync_source_hash_gate -v`
- `Get-Content src/services/pipeline_runtime.py`
- `rg -n "\\*\\*kwargs" index.py main.py src/entrypoints src/services`
