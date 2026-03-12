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
  - keep this as a test-contour experiment to prove or falsify Prometheus remote-write as the dominant bottleneck without changing prod behavior

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
