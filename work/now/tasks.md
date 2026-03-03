# Active Tasks

- [x] Activate `CAM-PIPELINE-CLEAN-SKELETON-V1` from priorities.
- [x] P01-T001: introduce shared `AppContext` contract (`src/app/context.py`) and wire bootstrap to it.
- [x] P01-T002: add baseline use-case contracts (`src/services/usecases/contracts.py`).
- [x] P02-T001: add thin `TimerJob.run(ctx)` scaffold (`src/entrypoints/jobs/timer_job.py`) without behavior change.
- [ ] P02-T002: adapt `main.py` to call `TimerJob` orchestration shell (feature-equivalent path).

## Blockers
- none

## Last Update
- 2026-03-04 (P02-T001 completed: added `TimerJob` linear orchestration scaffold, no behavior change yet)
