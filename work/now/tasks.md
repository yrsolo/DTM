# Active Tasks

- [x] Activate `CAM-PIPELINE-CLEAN-SKELETON-V1` from priorities.
- [x] P01-T001: introduce shared `AppContext` contract (`src/app/context.py`) and wire bootstrap to it.
- [x] P01-T002: add baseline use-case contracts (`src/services/usecases/contracts.py`).
- [x] P02-T001: add thin `TimerJob.run(ctx)` scaffold (`src/entrypoints/jobs/timer_job.py`) without behavior change.
- [x] P02-T002: adapt `main.py` to call `TimerJob` orchestration shell (feature-equivalent path).
- [x] P03-T001: classify runtime errors via typed app boundary (`TransientError` / `PermanentError` / `UserError`) without changing external API.
- [x] P03-T002: map typed errors to explicit entrypoint outcomes (HTTP/exit) in dedicated boundary layer.
- [ ] P04-T001: document pipeline skeleton/dataflow update in `docs/system/*` after first integration pass.

## Blockers
- none

## Last Update
- 2026-03-04 (P03 completed: typed errors now mapped to HTTP boundary outcomes for HTTP events; legacy fallback preserved)
