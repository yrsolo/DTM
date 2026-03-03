# Active Tasks

- [x] Activate `CAM-ENTRYPOINT-REFORM-V1` from priorities.
- [x] P01-T001: extract HTTP payload parsing into `src/entrypoints/http/event_parser.py` and delegate from `index.py`.
- [x] P01-T002: extract path/method/query parsing helpers from `index.py` into `src/entrypoints/http/event_parser.py`.
- [x] P01-T003: introduce HTTP router scaffold in `src/entrypoints/http/router.py` and delegate from `index.py`.
- [x] P02-T001: align `main.py` thin wrapper over `TimerJob` shell (feature-equivalent).
- [x] P02-T002: extract `db_migrate` branch into dedicated job module (`src/entrypoints/jobs/db_migrate_job.py`).
- [ ] P03-T001: extract migration sync/readmodel orchestration block from `main.py` into dedicated pipeline service module.

## Blockers
- none

## Last Update
- 2026-03-04 (P02 completed: `main.py` keeps timer shell + delegated `db_migrate` job, reducing entrypoint responsibility)
