# CAM-ENTRYPOINT-AND-PIPELINE-DEMONSTER-V1 Evidence

## Trust Gate
- source: runtime code (`index.py`, `src/entrypoints/http/*`, `src/services/pipeline_runtime.py`, `src/entrypoints/runtime/planner_runtime_entry.py`)
- last_verified_at: 2026-03-05
- verified_by: Codex
- trust_level: high
- evidence:
  - functional context dataclasses still present in HTTP/runtime modules
  - `SyncReadmodelPipelineContext` still present in `src/services/pipeline_runtime.py`
  - inline lambda wiring present in `index.py` and runtime pipeline setup
- notes:
  - prior V2 hygiene/dehybrid removed part of legacy coupling but left callback contexts

## Progress
- P01-T001: done
- P02-T001: done
- P03-T001: done
- P03-T002: done
- P03-T003: done
- P04-T001: done
- P04-T002: done
- P04-T003: done
- P05-T001: done (standard timer path no longer uses source-switch mutation injection)
- P06-T001: done
- P06-T002: done
- P06-T003: done

## Validation Log
- `python -m unittest tests.api.test_frontend_api_routing -v` -> OK (11 tests)
- `python -m unittest tests.api.test_frontend_api_v2_payload -v` -> OK (6 tests)
- `python -m unittest tests.services.test_pipeline_runtime -v` -> OK (4 tests)
- `python -m unittest tests.services.test_planner_pipeline_job -v` -> OK (1 test)
- `python -m unittest tests.services.test_sync_source_hash_gate -v` -> OK (8 tests)
- `python scripts/check_no_monsters.py` -> `check_no_monsters: OK`

## Removed runtime symbols
- `HttpRouterContext` removed from runtime route wiring.
- `GroupQueryHandlerContext` removed from runtime route wiring.
- `RuntimeExecutionContext` removed from runtime execution wiring.
- `SyncReadmodelPipelineContext` removed from runtime pipeline surface.

## Runtime contour after change
- `index.py` -> `HttpRouter(AppContext).dispatch(HttpRequest)` -> class handlers.
- `index.py` -> `RuntimeExecutor(AppContext).execute(...)` for non-HTTP planner modes.
- `planner_runtime_entry.py` -> `TimerPipeline(AppContext).run(RunRequest(...))`.
