# Active Tasks

- [x] Activate `CAM-ENTRYPOINT-REFORM-V1` from priorities.
- [x] P01-T001: extract HTTP payload parsing into `src/entrypoints/http/event_parser.py` and delegate from `index.py`.
- [x] P01-T002: extract path/method/query parsing helpers from `index.py` into `src/entrypoints/http/event_parser.py`.
- [x] P01-T003: introduce HTTP router scaffold in `src/entrypoints/http/router.py` and delegate from `index.py`.
- [x] P02-T001: align `main.py` thin wrapper over `TimerJob` shell (feature-equivalent).
- [x] P02-T002: extract `db_migrate` branch into dedicated job module (`src/entrypoints/jobs/db_migrate_job.py`).
- [x] P03-T001: extract migration sync/readmodel orchestration block from `main.py` into dedicated pipeline service module.
- [x] P03-T002: add focused unit smoke for extracted runtime pipeline helper (`run_ydb_sync_readmodel_pipeline`).
- [x] P04-T001: document entrypoint refactor progress in `docs/system/entrypoints_index_main.md` and prep closeout criteria.
- [ ] P04-T002: decide closeout threshold for CAM-ENTRYPOINT-REFORM-V1 (which blocks stay in `index.py/main.py` for next campaign).

## Blockers
- none

## Last Update
- 2026-03-04 (P04-T001 completed: `docs/system/entrypoints_index_main.md` now tracks concrete extraction progress for event parser/router)
