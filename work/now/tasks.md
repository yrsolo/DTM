# Active Tasks

- [x] Activate `CAM-CORE-CLEANUP-V1` from priorities.
- [x] P01-T001: inventory `core/*` modules and classify domain vs infra-coupled pieces (`docs/system/core_boundaries.md`).
- [x] P01-T002: map first atomic moves (`core/bootstrap.py`, `core/use_cases.py`) with concrete destination modules.
- [x] P02-T001: extract bootstrap/usecase implementation out of `core/` with compatibility shims.
- [ ] P02-T002: continue core cleanup by reducing direct runtime imports from `core/manager.py` and `core/repository.py` into service/adapters.

## Blockers
- none

## Last Update
- 2026-03-04 (P01 finished; P02-T001 completed with compatibility-preserving extraction to `src/app` and `src/services/usecases`)
