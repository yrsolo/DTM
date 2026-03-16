# Evidence - CAM-2026-03-12-DIRECT-API-OUTER-LATENCY-DECOMPOSITION-V1

## Trust gate
- source: active HTTP shell, dispatcher, frontend handler, observability layer
- last_verified_at: 2026-03-12
- verified_by: Codex
- evidence:
  - `src/entrypoints/index_dispatcher.py`
  - `src/entrypoints/http/http_shell.py`
  - `src/entrypoints/http/frontend_v2_handler.py`
  - `src/observability/bottlenecks.py`
- trust_level: high
- notes:
  - `bff` is intentionally out of scope

## Completed Tasks
- [x] `CAM-2026-03-12-DIRECT-API-OUTER-LATENCY-DECOMPOSITION-V1-P01-T001`
- [x] `CAM-2026-03-12-DIRECT-API-OUTER-LATENCY-DECOMPOSITION-V1-P01-T002`
- [x] `CAM-2026-03-12-DIRECT-API-OUTER-LATENCY-DECOMPOSITION-V1-P02-T001`
- [x] `CAM-2026-03-12-DIRECT-API-OUTER-LATENCY-DECOMPOSITION-V1-P02-T002`
- [x] `CAM-2026-03-12-DIRECT-API-OUTER-LATENCY-DECOMPOSITION-V1-P03-T001`
- [x] `CAM-2026-03-12-DIRECT-API-OUTER-LATENCY-DECOMPOSITION-V1-P03-T002`

## Verification
- local tests:
  - `python -m unittest tests.api.test_frontend_api_routing tests.api.test_info_observability tests.infra.test_grafana_specs`
- live test contour:
  - direct `GET /test/ops/api/v2/frontend?statuses=work,pre_done,done,wait&include_people=true&limit=60`
  - `/test/ops/info?format=json&view=detail`

## Live Findings
- profiling level on `test`: `stages`
- direct `/api` now exposes `Server-Timing` without payload contract changes
- recent outer traces are visible in `/info` detail under `bottlenecks.recentDirectApiOuterTraces`
- verified live trace on `2026-03-12`:
  - `function_total = 19186.840 ms`
  - `http_shell = 15832.407 ms`
  - `router_dispatch = 11977.469 ms`
  - `frontend_handler = 1176.014 ms`
  - `frontend_inner = 112.491 ms`
  - `frontend_unexplained = 19074.349 ms`
- latest matching recent outer trace in `/info` detail:
  - `traceId = 7a985f675c04`
  - `functionTotalMs = 19186.840`
  - `httpShellTotalMs = 15832.407`
  - `frontendInnerMs = 112.491`
  - `unexplainedInFunctionMs = 19074.349`

## Conclusion
- direct `/api` slowness is not explained by the cached inner frontend path
- current inner frontend work is about `112-130 ms`, while direct `/api` wall clock stays near `19 s`
- dominant latency sits in the outer function/shell/dispatch contour, not in payload build or masking
- next optimization wave should target direct `/api` outer runtime/infra overhead, not another inner query/cache refactor

## Notes
- latest known finding before this campaign: direct `/api` cache-hit inner frontend stages are about `129 ms`, so the dominant unexplained gap is outside the current inner handler path
