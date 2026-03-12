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
