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
- 2026-03-04: verification:
  - `rg "build_http_dispatch_handlers\\(" src index.py tests` -> only declaration left in `src/entrypoints/http/http_dispatch_chain.py`.
  - `python -m unittest tests.api.test_frontend_api_routing tests.api.test_frontend_api_v2_payload -v` passed.
  - `python -m unittest tests.services.test_pipeline_runtime tests.services.test_planner_pipeline_job tests.services.test_sync_source_hash_gate -v` passed.
