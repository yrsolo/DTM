# Active Tasks

- [x] Activate `CAM-CORE-CLEANUP-V1` from priorities.
- [x] P01-T001: inventory `core/*` modules and classify domain vs infra-coupled pieces (`docs/system/core_boundaries.md`).
- [x] P01-T002: map first atomic moves (`core/bootstrap.py`, `core/use_cases.py`) with concrete destination modules.
- [x] P02-T001: extract bootstrap/usecase implementation out of `core/` with compatibility shims.
- [x] P02-T002: remove `core.manager` dependency on `core.repository.TimingParser` via dedicated `core/timing_parser.py`.
- [ ] P02-T003: decide whether to fully de-duplicate `TimingParser` implementation in `core/repository.py` (now two copies) without behavior drift.

## Blockers
- none

## Last Update
- 2026-03-04 (P02-T002 completed: `core/manager.py` now imports parser from `core/timing_parser.py`, reducing repository coupling)
