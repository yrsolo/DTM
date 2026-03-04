# CAM-ENTRYPOINT-DEHYBRID-V1 Evidence

## Trust Registry
| source | last_verified_at | verified_by | evidence | trust_level | notes |
|---|---|---|---|---|---|
| `index.py`, `main.py`, `src/entrypoints/http/*`, `src/entrypoints/jobs/*`, `src/services/pipeline_runtime.py` | 2026-03-04 | TeamLead agent | direct code scan (`rg` + file reads) | high | confirms coupling `index -> main` and mixed legacy/modern imports at campaign start |
| `tests/api/test_frontend_api_routing.py`, `tests/services/test_pipeline_runtime.py`, `tests/services/test_planner_pipeline_job.py`, `tests/services/test_sync_source_hash_gate.py` | 2026-03-04 | TeamLead agent | direct test contour scan | high | confirms minimum smoke contour for dehybrid steps |

## Execution Log
- `DEHYBRID-P01-T001` completed: removed direct `index -> main` coupling by introducing shared runtime entry module `src/entrypoints/runtime/planner_runtime_entry.py`.
- `DEHYBRID-P01-T002` completed: `index.py` now dispatches runtime through shared entry function (`run_planner_runtime`) instead of importing `main.main`.

## Verification
- `rg -n "from main import main|main_func=main" index.py src tests`
- `python -m unittest tests.api.test_frontend_api_routing tests.services.test_pipeline_runtime tests.services.test_planner_pipeline_job tests.services.test_sync_source_hash_gate -v`
- `python -m py_compile index.py main.py src/entrypoints/runtime/planner_runtime_entry.py`
