# CAM-ENTRYPOINT-HYGIENE-V2 Evidence

## Trust Gate
- source: `index.py`, `main.py`, `src/entrypoints/http/*`, `src/services/pipeline_runtime.py`
- last_verified_at: 2026-03-04
- verified_by: codex
- evidence: post-dehybrid runtime scan and signature audit initiated
- trust_level: high
- notes: campaign activated after DEHYBRID-V2 archive.

## Execution Log
- 2026-03-04: campaign activated.
- 2026-03-04: trust-gate scan done for entrypoints/services hyperfunction contour.
  - runtime still had handler-factory contour `build_http_dispatch_handlers(...)`.
- 2026-03-04: runtime switched to object router:
  - `src/entrypoints/http/router.py` now provides `HttpRouterContext` + `HttpRouter`.
  - `index.py` now calls `HttpRouter(ctx).dispatch(event, is_http_event)`.
  - `build_http_dispatch_handlers(...)` remains only as legacy module (not in runtime path).
- 2026-03-04: timer sync pipeline switched to object wrapper:
  - added `TimerPipeline` in `src/services/pipeline_runtime.py`
  - `planner_pipeline_job` now builds sync context/request and calls `TimerPipeline(...).run(...)`.
- 2026-03-04: aligned AppContext as dependency carrier for entrypoint runtime bindings:
  - `src/app/bootstrap.py` now injects runtime bindings (`key_json`, `sheet_info`, YDB creds/endpoint, TG bindings, migration toggles) into `AppContext.deps`.
  - `index.py` and `src/entrypoints/runtime/planner_runtime_entry.py` consume these bindings from `APP_CONTEXT.deps` instead of direct `from config import ...`.
- 2026-03-04: removed dead runtime dispatch factory module `src/entrypoints/http/http_dispatch_chain.py` after `HttpRouter` migration.
- 2026-03-04: reduced active runtime hyperfunction signatures:
  - `FrontendV2HandlerContext` + `FrontendV2Handler` introduced in `src/entrypoints/http/frontend_v2_handler.py`.
  - `RuntimeContextRequest` introduced in `src/entrypoints/jobs/runtime_context_job.py`.
  - `ReadmodelProbeRequest` introduced in `src/entrypoints/jobs/readmodel_probe_job.py`.
  - `planner_runtime_entry.py` switched to request DTO calls for runtime-context/probe jobs.
- 2026-03-04: verification:
  - `rg "build_http_dispatch_handlers\\(" src index.py tests` -> no matches in runtime tree.
  - `rg "from config import" index.py src/entrypoints/runtime/planner_runtime_entry.py` -> no matches.
  - long-signature audit (`args>7`) now reports only legacy-mode jobs:
    - `src/entrypoints/jobs/legacy_store_write_job.py`
    - `src/entrypoints/jobs/planner_setup_job.py`
    - `src/entrypoints/jobs/source_switch_job.py`
  - `python -m unittest tests.api.test_frontend_api_routing tests.api.test_frontend_api_v2_payload -v` passed.
  - `python -m unittest tests.services.test_pipeline_runtime tests.services.test_planner_pipeline_job tests.services.test_sync_source_hash_gate -v` passed.
