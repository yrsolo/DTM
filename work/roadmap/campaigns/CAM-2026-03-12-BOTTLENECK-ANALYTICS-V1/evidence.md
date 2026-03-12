# Evidence - CAM-2026-03-12-BOTTLENECK-ANALYTICS-V1

## Trust gate
- source: active runtime code, existing observability docs, current Grafana spec
- last_verified_at: 2026-03-12
- verified_by: Codex
- evidence:
  - `src/entrypoints/http/frontend_v2_handler.py`
  - `src/observability/*`
  - `src/entrypoints/http/info_handler.py`
  - `src/infra/grafana_specs.py`
- trust_level: high
- notes:
  - this campaign is repo-native; no imported evidence is reused

## Completed Tasks
- [x] `CAM-2026-03-12-BOTTLENECK-ANALYTICS-V1-P01-T001`
- [x] `CAM-2026-03-12-BOTTLENECK-ANALYTICS-V1-P01-T002`
- [x] `CAM-2026-03-12-BOTTLENECK-ANALYTICS-V1-P02-T001`
- [x] `CAM-2026-03-12-BOTTLENECK-ANALYTICS-V1-P02-T002`
- [x] `CAM-2026-03-12-BOTTLENECK-ANALYTICS-V1-P02-T003`
- [x] `CAM-2026-03-12-BOTTLENECK-ANALYTICS-V1-P03-T001`
- [x] `CAM-2026-03-12-BOTTLENECK-ANALYTICS-V1-P03-T002`
- [x] `CAM-2026-03-12-BOTTLENECK-ANALYTICS-V1-P03-T003`

## Verification
- Command:
  - `python -m unittest tests.observability.test_metrics_batching tests.config.test_runtime_loader`
  - `python -m unittest tests.api.test_frontend_api_routing tests.api.test_info_observability tests.infra.test_grafana_specs`
- Result:
  - local config, observability, frontend, `/info`, and Grafana spec coverage passed on 2026-03-12

## Notes
- profiling policy now distinguishes `off`, `stages`, and `debug`
- frontend stage traces are intended for bottleneck localization, not as a permanent high-cardinality metrics surface

## Live verification (2026-03-12)
- deployed commit to `origin/test`: `a51a325315d47c9286152f82d76dbe76feffe335`
- Grafana test dashboard was republished from repo spec with:
  - `python scripts/provision_grafana_dashboard.py --env test`
- live `/info` confirmation on `test`:
  - `bottlenecks.profilingLevel=stages`
  - `telemetry.bottleneckMetricsLevel=stages`
- live same-connection trace capture for direct API default query:
  - request: `/test/ops/api/v2/frontend?statuses=work,pre_done,done,wait&include_people=true&limit=60`
  - wall clock observed from shell: about `12175 ms`
  - recent trace from `/test/ops/info?format=json&view=detail`:
    - `route=api`
    - `cacheResult=hit`
    - `totalTrackedMs=128.793`
    - dominant tracked stage: `prep_snapshot_access=95.419 ms`
    - second stage: `response_cache_read=27.256 ms`
- live same-connection trace capture for browser-proxy route:
  - request: `/test/ops/bff/api/v2/frontend?statuses=work,pre_done,done,wait&include_people=true&limit=60`
  - wall clock observed from shell: about `14154 ms`
  - recent trace from `/test/ops/info?format=json&view=detail`:
    - `route=bff`
    - `cacheResult=hit`
    - `totalTrackedMs=132.314`
    - dominant tracked stage: `prep_snapshot_access=91.001 ms`
    - second stage: `response_cache_read=35.917 ms`
- conclusion:
  - cache-hit backend tracked stages are currently around `129-132 ms`
  - remaining user-visible `12-14 s` latency sits outside tracked backend stage work
  - current dominant unexplained budget is therefore in outer runtime/infra contour (serverless cold path, ingress/proxy, connection setup, or other non-instrumented wrapper overhead), not in frontend payload build or cache-hit masking path
