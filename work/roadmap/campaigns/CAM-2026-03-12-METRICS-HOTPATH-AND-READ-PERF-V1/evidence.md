# Evidence - CAM-2026-03-12-METRICS-HOTPATH-AND-READ-PERF-V1

## Trust gate
- source: owner-provided reference bundle, verified code paths, active observability docs
- last_verified_at: 2026-03-12
- verified_by: Codex
- evidence:
  - `agent/intructions/DTM-test/work/roadmap/MASTER_EXECUTION_BRIEF_2026-03-12.md`
  - `src/observability/*`
  - `src/entrypoints/http/info_handler.py`
  - `src/worker/*`
- trust_level: medium
- notes:
  - imported campaign evidence is not reused as-is
  - performance claims must be re-measured from active code and live contour

## Baseline findings to verify
- hot paths may still pay sync metric cost on more than one backend
- refresh wall-clock and visible `/info` timing are not yet decomposed cleanly
- `/info` default path may still include expensive diagnostics by default
- common frontend request has no verified prebuilt hot cache

## Follow-up scope opened (2026-03-12)
- active follow-up: exact default frontend response cache in Object Storage for:
  - browser proxy path class
  - direct backend path class
  - `full`
  - `masked`
- exact default query for cache eligibility:
  - `statuses=work,pre_done,done,wait`
  - `include_people=true`
  - `limit=60`
  - no designer filter
  - no window filter
- memory cache is explicitly out because runtime is serverless
- masking follow-up:
  - deterministic mapping remains required within one bucket
  - masked mapping bucket will rotate by Moscow hour

## Verified execution findings
- 2026-03-12 code scan: `src/entrypoints/http/info_handler.py` previously built snapshot/build/storage/queue/jobs payload on every `/info` request, so default `/info` was not lightweight
- 2026-03-12 implementation: `/info` now returns cheap `view=summary` by default and uses explicit detail mode for heavy diagnostics:
  - query form: `/info?view=detail`
  - path forms: `/info/detail`, `/api/v2/info/detail`
- 2026-03-12 implementation: HTML dashboard keeps working by explicitly loading `/info?format=json&view=detail` from client-side JS, while the initial page response remains lightweight
- 2026-03-12 implementation: `dtm.info.summary.ms` and `dtm.info.detail.ms` are emitted separately from `InfoHandler.handle()`
- 2026-03-12 local contract smoke passed:
  - `python -m unittest tests.api.test_info_observability`
  - `python -m unittest tests.api.test_frontend_api_routing`
- 2026-03-12 code scan: refresh wall-clock metrics already exist in active runtime paths:
  - `src/jobs/update_snapshot_job.py` emits `dtm.snapshot.job_wall_clock_ms`
  - `src/worker/worker.py` emits `dtm.worker.wall_clock_ms`
  - `src/observability/batching.py` emits `dtm.metrics.flush_duration_ms`
  - `src/entrypoints/http/http_shell.py` emits `dtm.api.duration_ms`
- 2026-03-12 implementation follow-up: exact default frontend response cache was added in Object Storage for common frontend read path:
  - exact query: `statuses=work,pre_done,done,wait`, `include_people=true`, `limit=60`
  - shared cache variants: `full` and `masked`
  - route classes: trusted ingress (`bff`) and direct backend (`api`)
  - storage namespace: dedicated `snapshot_engine.prefix_responses`
- 2026-03-12 implementation follow-up: masked mapping seed now rotates by Moscow hour for all masked frontend responses while staying deterministic within the same hour bucket
- 2026-03-12 local cache/masking smoke passed:
  - `python -m unittest tests.api.test_frontend_api_routing`
  - `python -m unittest tests.snapshot_engine.test_s3_store`
  - `python -m unittest tests.services.test_masking`
  - `python -m unittest tests.api.test_info_observability`

## Remaining verification
- live contour benchmark is still required after deploy to compare:
  - default summary `/info`
  - explicit detail `/info?view=detail`
- hot cache implementation now exists locally, but live contour verification is still required for:
  - cache warm-up on default frontend query
  - cache hit on repeated default frontend query
  - masked hourly seed rollover behavior
- refresh wall-clock gap still needs evidence write-up that correlates job timings, worker wall clock, and metrics flush duration on the same run

## Live verification (2026-03-12)
- deployed commit to `origin/test`: `c1dda7cee93d7dc2f2caceb0343f380890a32922`
- GitHub Actions test deploy:
  - failed first run for `22abbf9541110c7bab9e1e2ad4c293c87ee05b00` because `index.py` violated entrypoint guard scripts
  - fixed in follow-up commit `c1dda7c`
  - successful run: `Deploy Yandex Cloud Function (test contour)` run `22990483355`
- live contract verification against `https://dtm.solofarm.ru/test/ops/info`:
  - `?format=json` now returns `view=summary`
  - `?format=json&view=detail` now returns `view=detail`
  - summary payload exposes `counts.detailDeferred=true`
- live wall-clock spot check from shell, 3 requests each:
  - summary: `2804` bytes, about `2581-3343 ms`
  - detail: `31336` bytes, about `3334-4722 ms`
- conclusion:
  - summary/detail split is live and externally visible
  - detail payload is materially heavier by payload size and slower in the worst sampled request
  - dedicated live timing metrics exist in code path, but flush-overhead and refresh-gap evidence still need separate monitoring correlation

## Live refresh evidence (2026-03-12)
- triggered live test refresh through `POST https://dtm.solofarm.ru/test/ops/admin/commands/update-snapshot`
- observed job:
  - `job_id`: `d30be4de462343faa7ba2f09d2ff1c8b`
  - `status`: `success`
  - `requested_at_utc`: `2026-03-12T07:36:17+00:00`
  - `started_at_utc`: `2026-03-12T07:36:22+00:00`
  - `finished_at_utc`: `2026-03-12T07:36:29+00:00`
- reported live timings from job summary:
  - `job_wall_clock_ms`: `5889.699`
  - `timings_ms.total_duration_ms`: `4225.613`
  - dominant stage: `fetch_sheet_ms` about `2601.367`
  - write stages: `write_raw_ms` about `358.008`, `write_prep_ms` about `292.423`
- derived interpretation:
  - queue/start delay from request to worker start: about `5000 ms`
  - in-worker gap between `job_wall_clock_ms` and `total_duration_ms`: about `1664 ms`
  - this gap is consistent with wrapper overhead outside core snapshot update, including task-source setup and metrics flush path, but public surfaces still do not isolate flush-only duration

## Default frontend response cache live smoke (2026-03-12)
- deployed commit to `origin/test`: `8cf4775`
- default exact query under test:
  - `statuses=work,pre_done,done,wait`
  - `include_people=true`
  - `limit=60`
- live shell smoke after deploy:
  - direct API `https://dtm.solofarm.ru/test/ops/api/v2/frontend?...`
    - first hit: about `8.89s`, `77469` bytes
    - second hit: about `3.33s`, `77469` bytes
  - browser proxy `https://dtm.solofarm.ru/test/ops/bff/api/v2/frontend?...`
    - first hit: about `4.96s`, `72299` bytes
    - second hit: about `3.83s`, `72299` bytes
- interpretation:
  - exact default query cache seam is live on `test`
  - repeated request after warm-up is materially faster on both direct and proxy contours
  - `api` and `bff` payload sizes differ as expected because `bff` guest path remains masked while direct API still returns its own access context

## Hourly masking seed verification (2026-03-12)
- local deterministic proof:
  - same Moscow hour -> same masking version
  - next Moscow hour -> different masking version
- covered by:
  - `python -m unittest tests.services.test_masking`
- live cross-hour contour verification is still pending a natural hour rollover or an injected controllable clock seam

## Current blocker
- separate live quantification of `dtm.metrics.flush_duration_ms` is blocked by missing read access to monitoring data:
  - `/info` exposes config and dashboard links, not raw metric samples
  - current public Grafana dashboard token exposes dashboard JSON, but the published panel set does not expose flush-duration panels or raw query results for them
  - repo code confirms flush metrics are emitted, but active contour evidence cannot isolate their live value without monitoring/Grafana query access

## Test-only Prometheus A/B follow-up (2026-03-13)
- local A/B verification on the same direct `/api/v2/frontend` request shows that synchronous Prometheus remote-write can dominate latency:
  - `PROMETHEUS_ENABLED=0` local average: about `2812 ms`
  - `PROMETHEUS_ENABLED=1` local average: about `37190 ms`
- live `test` direct `/api` requests before override also showed the same shape:
  - wall clock about `25-33s`
  - `frontend_inner` stayed sub-second to low-second
  - `frontend_handler`, `function_total`, `unexplained_inside_handler`, and `unexplained_after_handler` ballooned into multi-second ranges
- follow-up decision:
  - override `PROMETHEUS_ENABLED=false` only in `.github/workflows/deploy_yc_function_main.yml`
  - then local follow-up showed `MONITORING_ENABLED=1` by itself can also stall the request path into `~28.9s` with repeated sync `monitoring_metric_flush_failed`
  - final test-contour experiment disables both remote metrics backends in the test deploy workflow without changing prod behavior

## Buffered metrics delivery redesign (2026-03-13)
- implemented locally:
  - new runtime config key `runtime.metrics_delivery_mode` with default `buffered`
  - env override `METRICS_DELIVERY_MODE=off|buffered`
  - `build_app_context()` now wires:
    - `metrics_sink` as remote backend sink (`Noop`, `Monitoring`, `Prometheus`, `Composite`)
    - `metrics_client` as `BufferedMetricsClient(metrics_sink)` by default
    - `NoopMetricsClient` immediately when `metrics_delivery_mode=off`
- request path change:
  - `src/entrypoints/http/http_shell.py` now wraps the whole HTTP request in a managed buffered metrics scope and performs one best-effort flush at the end of the request
- job/worker alignment:
  - `Worker.run_once_from_messages()` and `UpdateSnapshotJob.run()` now execute under the same managed buffered scope, so batch collectors append into one buffered request/job batch instead of triggering per-metric remote writes
- telemetry contract:
  - `/info` telemetry block now exposes `metricsDeliveryMode`, `metricsSink`, and `remoteMetricsEnabled`
- local contract verification passed:
  - `.venv\Scripts\python.exe -m unittest tests.config.test_runtime_loader`
  - `.venv\Scripts\python.exe -m unittest tests.app.test_bootstrap_monitoring`
  - `.venv\Scripts\python.exe -m unittest tests.observability.test_metrics_batching`
  - `.venv\Scripts\python.exe -m unittest tests.observability.test_prometheus_metrics`
  - `.venv\Scripts\python.exe -m unittest tests.observability.test_yandex_monitoring_metrics`
  - `.venv\Scripts\python.exe -m unittest tests.api.test_frontend_api_routing`
  - `.venv\Scripts\python.exe -m unittest tests.api.test_info_observability`
  - `.venv\Scripts\python.exe -m unittest tests.api.test_command_queue_foundation`
  - `.venv\Scripts\python.exe -m unittest tests.api.test_worker_shell`
- rollout step prepared:
  - `.github/workflows/deploy_yc_function_main.yml` restored `MONITORING_ENABLED=true` and `PROMETHEUS_ENABLED=true` for `test`
- pending evidence:
  - none

## Live verification after buffered redesign (2026-03-13)
- deployed commit to `origin/test`: `b20a189`
- deploy workflow restored:
  - `MONITORING_ENABLED=true`
  - `PROMETHEUS_ENABLED=true`
- rollout confirmation:
  - `/test/ops/info?format=json&view=detail` now reports:
    - `telemetry.metricsDeliveryMode=buffered`
    - `telemetry.metricsClient=BufferedMetricsClient`
    - remote metrics backends enabled again on `test`
- direct `/test/ops/api/v2/frontend?statuses=work,pre_done,done,wait&include_people=true&limit=60` live samples after redeploy:
  - run 1: wall `6564.1 ms`, `frontend_handler=830.300 ms`, `frontend_inner=829.645 ms`, `function_total=2489.132 ms`
  - run 2: wall `2063.5 ms`, `frontend_handler=106.911 ms`, `frontend_inner=104.563 ms`, `function_total=835.877 ms`
  - run 3: wall `2321.3 ms`, `frontend_handler=166.763 ms`, `frontend_inner=163.700 ms`, `function_total=1179.186 ms`
  - run 4: wall `2696.9 ms`, `frontend_handler=110.244 ms`, `frontend_inner=108.099 ms`, `function_total=1154.438 ms`
  - run 5: wall `1544.5 ms`, `frontend_handler=156.691 ms`, `frontend_inner=154.438 ms`, `function_total=717.315 ms`
- interpretation:
  - buffered delivery removes the previous `15-35s` request-path blow-up with remote backends enabled
  - `frontend_inner` stays low and close to `frontend_handler`
  - remaining wall clock is no longer dominated by synchronous per-metric backend writes
- update-snapshot smoke after redesign:
  - `POST /test/ops/admin/commands/update-snapshot` accepted in `1765.8 ms`
  - resulting job `de41269494fe4680b0d40a673cafe46b` finished `success`
  - summary:
    - `job_wall_clock_ms=5143.91`
    - `timings_ms.total_duration_ms=4084.1862450000017`
- conclusion:
  - buffered metrics delivery is sufficient to re-enable remote metrics backends on `test`
  - direct `/api` regression from synchronous per-metric flush is closed

## API metrics suppression follow-up (2026-03-13)
- owner decision: remove API-path remote metrics for now and keep metrics only on refresh/render/worker paths
- implementation:
  - `config/runtime.yaml` now sets `monitoring.emit_api_metrics=false`
  - `src/observability/bottlenecks.py` suppresses `dtm.api.stage.*` and `dtm.api.outer.*` writes when API metrics are disabled, while preserving in-process trace recording
  - `src/entrypoints/http/http_shell.py`, `src/entrypoints/http/frontend_v2_handler.py`, and `src/entrypoints/http/info_handler.py` no longer emit `dtm.api.*` / `dtm.info.*` when API metrics are disabled
- preserved diagnostics:
  - `Server-Timing`
  - `RECENT_API_STAGE_EVENTS`
  - `RECENT_DIRECT_API_OUTER_TRACES`
  - `/info` bottleneck diagnostics
- local contract verification passed:
  - `.venv\Scripts\python.exe -m unittest tests.api.test_frontend_api_routing tests.api.test_info_observability`
  - `.venv\Scripts\python.exe -m unittest tests.app.test_bootstrap_monitoring tests.config.test_runtime_loader tests.observability.test_metrics_batching tests.api.test_command_queue_foundation tests.api.test_worker_shell`

## Live verification after API metrics suppression (2026-03-13)
- deployed commit to `origin/test`: `2d9d04d`
- telemetry on `/test/ops/info?format=json&view=detail` confirms buffered delivery still active:
  - `telemetry.metricsDeliveryMode=buffered`
  - `telemetry.metricsSink=CompositeMetricsClient`
  - `telemetry.remoteMetricsEnabled=true`
- direct `/test/ops/api/v2/frontend?statuses=work,pre_done,done,wait&include_people=true&limit=60` live samples after suppressing `dtm.api.*` / `dtm.info.*` writes:
  - run 1: wall `8809.5 ms`, response body `68249 B`
  - run 2: wall `2796.9 ms`, response body `68249 B`
  - run 3: wall `3081.2 ms`, response body `68249 B`
  - run 4: wall `3431.5 ms`, response body `68249 B`
  - run 5: wall `4559.1 ms`, response body `68249 B`
- representative direct `/api` response headers now show only timing diagnostics, not API metrics writes:
  - `server-timing: router_precheck;dur=0.02, router_handler;dur=650.749, router_total;dur=650.801, http_shell_post_router;dur=0.014, response_build;dur=0.003, frontend_handler;dur=647.812, frontend_inner;dur=595.669, function_total;dur=651.147, unexplained_inside_handler;dur=52.143, unexplained_after_handler;dur=3.335`
- `/info` bottleneck recorder still works with API metrics suppressed:
  - `recentApiTraces_count=8`
  - `recentDirectApiOuterTraces_count=8`
- interpretation:
  - removing remote API metrics keeps `Server-Timing` and in-process traces intact
  - direct `/api` no longer pays the previous remote observability tax from `dtm.api.*` / `dtm.info.*`
  - refresh/render/worker observability remains enabled through buffered remote sinks

## Grafana dashboard rebuild (2026-03-12)
- repo spec in `src/infra/grafana_specs.py` was rebuilt to cover all currently emitted runtime metrics from active code paths:
  - snapshot stages including `orphan_reconcile`
  - snapshot duration, wall clock, and flush duration
  - render duration, wall clock, total, rows, and cells
  - API duration and response size
  - `dtm.info.summary.ms` and `dtm.info.detail.ms`
  - notify totals and runtime metrics
  - telegram updates/accepted/rejected/enqueue/command metrics
  - worker totals, failures, retries, command duration, wall clock
  - flush duration, points, and failures
- compact layout change:
  - single-value stat panels reduced from `4x4` to `2x2`
  - time-series panels reduced from `12` columns wide to `6` columns wide
- live republish performed with:
  - `python scripts/provision_grafana_dashboard.py --env test`
- live public dashboard verification through `GET /grafana/api/public/dashboards/af7606b66c8d4ca9b069ea1913577e45` confirms:
  - `Snapshot Fetch Last` is now `2x2`
  - new compact stat panels are present for `Orphan Reconcile Last`, `Timeline Wall Clock Last`, `Designers Wall Clock Last`, `Info Summary Last`, `Info Detail Last`
  - new compact charts are present for `API and Info Latency` and `Metrics Flush Volume`

## Info page compact controls (2026-03-12)
- `/test/ops/info` now renders these sections as collapsed by default:
  - `Recent Jobs`
  - `Admin Actions`
  - `API Request Builder`
  - `Info JSON`
- live HTML verification confirms four collapsed `details.card.section.collapsible` sections are present on the test contour

## Required evidence during execution
- call graph of metric backend writes
- before/after refresh timings by stage
- before/after info summary vs detail timings
- benchmark of default `/info` summary
- benchmark of explicit detail mode
- proof of separate `info.summary.ms` and `info.detail.ms`
- before/after frontend request timings by stage

## Risks
- extra instrumentation can distort timings
- queue lag and backend variability can dominate some runs
