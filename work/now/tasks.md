# Active Tasks

- [x] Activate `CAM-ENTRYPOINT-REFORM-V1` from priorities.
- [x] P01-T001: extract HTTP payload parsing into `src/entrypoints/http/event_parser.py` and delegate from `index.py`.
- [ ] P01-T002: extract path/method/query parsing helpers from `index.py` into `src/entrypoints/http/event_parser.py`.
- [ ] P01-T003: introduce HTTP router scaffold in `src/entrypoints/http/router.py` and delegate from `index.py`.
- [ ] P02-T001: align `main.py` thin wrapper over `TimerJob` shell (feature-equivalent).

## Blockers
- none

## Last Update
- 2026-03-04 (P01-T001 completed: `_extract_payload` moved out of `index.py` into `src/entrypoints/http/event_parser.py`)
