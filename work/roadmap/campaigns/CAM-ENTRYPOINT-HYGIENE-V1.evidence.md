# CAM-ENTRYPOINT-HYGIENE-V1 Evidence

## Trust Registry
| source | last_verified_at | verified_by | evidence | trust_level | notes |
|---|---|---|---|---|---|
| `index.py`, `src/entrypoints/http/http_dispatch_chain.py`, `src/entrypoints/http/runtime_execution.py`, `src/entrypoints/jobs/planner_pipeline_job.py`, `src/services/pipeline_runtime.py` | 2026-03-04 | TeamLead agent | direct code scan (`rg` + file reads) | high | hyperfunction signatures confirmed in active runtime path |
| `tests/api/test_frontend_api_routing.py`, `tests/services/test_pipeline_runtime.py`, `tests/services/test_planner_pipeline_job.py` | 2026-03-04 | TeamLead agent | direct smoke contour scan | high | baseline verification set for hygiene refactors |

## Execution Log
- `HYGIENE-P01-T001` completed: trust-gate baseline captured; identified parameter-sheet hotspots in HTTP dispatch and runtime pipeline functions.
- `HYGIENE-P02-T001` completed: introduced `HttpDispatchHandlersContext` to collapse `build_http_dispatch_handlers(...)` argument sheet into a typed context object; `index.py` wiring switched to context construction.

## Verification
- `rg -n "^def |^async def " src/entrypoints src/services | rg -n "build_http_dispatch_handlers|execute_runtime|run_planner_pipeline|run_ydb_sync_readmodel_pipeline|run_planner_runtime|dispatch_http|handle_group_query_if_requested"`
- `Get-Content src/entrypoints/http/http_dispatch_chain.py`
- `Get-Content src/entrypoints/http/runtime_execution.py`
- `Get-Content src/entrypoints/jobs/planner_pipeline_job.py`
- `Get-Content src/services/pipeline_runtime.py`
- `python -m unittest tests.api.test_frontend_api_routing tests.services.test_pipeline_runtime tests.services.test_planner_pipeline_job -v`
