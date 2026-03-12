# Evidence - CAM-2026-03-12-DIRECT-API-TRUSTWORTHY-DIAGNOSTICS-V1

## Trust gate
- source: direct `/api` router, shell, dispatcher, frontend handler, observability layer
- last_verified_at: 2026-03-12
- verified_by: Codex
- evidence:
  - `src/entrypoints/http/router.py`
  - `src/entrypoints/http/http_shell.py`
  - `src/entrypoints/index_dispatcher.py`
  - `src/entrypoints/http/frontend_v2_handler.py`
  - `src/observability/bottlenecks.py`
- trust_level: high
- notes:
  - `bff` remains out of scope

## Completed Tasks
- [x] `CAM-2026-03-12-DIRECT-API-TRUSTWORTHY-DIAGNOSTICS-V1-P01-T001`
- [x] `CAM-2026-03-12-DIRECT-API-TRUSTWORTHY-DIAGNOSTICS-V1-P01-T002`
- [x] `CAM-2026-03-12-DIRECT-API-TRUSTWORTHY-DIAGNOSTICS-V1-P02-T001`
- [x] `CAM-2026-03-12-DIRECT-API-TRUSTWORTHY-DIAGNOSTICS-V1-P02-T002`
- [x] `CAM-2026-03-12-DIRECT-API-TRUSTWORTHY-DIAGNOSTICS-V1-P03-T001`
- [x] `CAM-2026-03-12-DIRECT-API-TRUSTWORTHY-DIAGNOSTICS-V1-P03-T002`

## Verification
- local tests:
  - `python -m unittest tests.api.test_frontend_api_routing`
  - `python -m unittest tests.api.test_info_observability`
  - `python -m unittest tests.infra.test_grafana_specs`
- deploy:
  - commit `fbe55ee` opened the wave on `test`
  - commit `ee216e2` aligned `frontend_handler` timing with the same boundary used by router timing and removed leaked internal timing headers from public responses
- live `test` direct `/api` request:
  - request: `https://dtm.solofarm.ru/test/ops/api/v2/frontend?statuses=work,pre_done,done,wait&include_people=true&limit=60`
  - final `Server-Timing` sample:
    - `router_precheck=0.034 ms`
    - `router_handler=14444.958 ms`
    - `router_total=14445.030 ms`
    - `http_shell_post_router=1311.699 ms`
    - `frontend_handler=13271.248 ms`
    - `frontend_inner=613.183 ms`
    - `function_total=25974.413 ms`
    - `unexplained_inside_handler=12658.065 ms`
    - `unexplained_after_handler=12703.165 ms`
  - public response no longer leaked `X-DTM-Router-*`, `X-DTM-Frontend-*`, or `X-DTM-Trace-Id`; only `Server-Timing` remained in `stages` mode
- live `test` `/info?format=json&view=detail` trace:
  - `functionTotalMs=26718.224`
  - `routerPrecheckTotalMs=0.040`
  - `routerHandlerTotalMs=17331.247`
  - `routerTotalMs=17331.323`
  - `httpShellPostRouterMs=1733.755`
  - `frontendHandlerTotalMs=14641.090`
  - `frontendInnerCoreMs=147.866`
  - `unexplainedInsideHandlerMs=14493.224`
  - `unexplainedAfterHandlerMs=12077.134`
- conclusion:
  - diagnostics are now internally trustworthy enough for optimization planning
  - dominant latency is not in router precheck or inner frontend payload work
  - dominant latency is split between:
    - `unexplained_inside_handler` after core frontend stages but before handler return
    - `unexplained_after_handler` after handler return but before function completion
