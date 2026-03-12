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

## Remaining verification
- live contour benchmark is still required after deploy to compare:
  - default summary `/info`
  - explicit detail `/info?view=detail`
- hot cache decision remains open until real read-path timings are captured from the active contour
- refresh wall-clock gap still needs evidence write-up that correlates job timings, worker wall clock, and metrics flush duration on the same run

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
