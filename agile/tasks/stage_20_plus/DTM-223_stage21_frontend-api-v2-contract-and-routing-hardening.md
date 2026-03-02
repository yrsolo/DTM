# DTM-223: Stage 21 frontend API v2 contract and routing hardening

## Context
- API v1 endpoints exist, but real gateway event shapes caused route misses and `dtm_runtime_noop`.
- New expandable API contract v2 is required in parallel to v1 (strangler pattern).
- DB migration status is fixed and parked; focus is API contract and transport robustness.

## Goal
- Keep v1 stable and working.
- Add v2 endpoints and payload contract (`meta + filters + summary + entities + tasks`).
- Add docs and tests to prevent contract drift.

## Non-goals
- No breaking change for v1 consumers.
- No full switch to YDB as default read source in this task.

## Plan
1. Stage A: harden request parsing/path/query + debug flag and real fixture tests.
2. Stage B: add v2 contract docs and compatibility changelog.
3. Stage C: implement `/api/v2/frontend` and `/api/v2/frontend/doc` + v2 mapper.
4. Stage D: add structure validation and snapshot test for v2 payload.
5. Stage E: add `FRONTEND_API_DEFAULT_VERSION` flag and API observability logs.

## Checklist (DoD)
- [x] v1 routes parse real gateway event shape and return payload (not noop) on fixture.
- [x] `/api/v2/frontend` and `/api/v2/frontend/doc` implemented and documented.
- [x] v2 payload includes stable `meta.hash` and optional `tasks[].hash/revision` placeholders.
- [x] tests added: routing/query parser, v2 snapshot, v1 backward smoke.
- [x] shared task query contract introduced and reused across API payloads, sheet render, and reminder date selection.
- [x] README updated with v1/v2 endpoint references.
- [ ] Cloud verification pending test deploy (`git_ref=dev`).

## Work log
- 2026-03-02: Task created, execution started.
- 2026-03-02: Added v2 mapper (`core/api_payload_v2.py`) with stable `meta.hash`, entities/tasks model and reserved `hash/revision` task fields.
- 2026-03-02: Added v2 routes and docs handlers in `index.py` (`/api/v2/frontend`, `/api/v2/frontend/doc`).
- 2026-03-02: Hardened v1/v2 request parsing for Yandex gateway event variants (`pathParams.proxy`, `params.proxy`, multi-value query maps, raw query/url parse).
- 2026-03-02: Added docs `docs/api/frontend-v2.md` and `docs/api/changelog.md`.
- 2026-03-02: Added tests and fixtures:
  - `tests/fixtures/http_event_yc_api_gw.json`
  - `tests/api/test_frontend_api_routing.py`
  - `tests/api/test_frontend_api_v2_payload.py`
  - `tests/snapshots/frontend_v2_payload.json`
- 2026-03-02: Added `FRONTEND_API_DEFAULT_VERSION` + `DEBUG_HTTP_EVENT` env contour and updated `.env.example`.
- 2026-03-02: Added lightweight Actions deps split `requirements.actions.txt` and switched deploy/release workflows.
- 2026-03-02: Added shared query contract module `core/task_query_contract.py` and removed duplicated status/designer/window/milestone filtering from `core/api_payload.py`, `core/api_payload_v2.py`, `core/manager.py`, `core/planner.py`, and `core/reminder.py`.
- 2026-03-02: Added contract test `tests/test_task_query_contract.py` and refreshed v2 snapshots.

## Links
- `index.py`
- `core/api_payload.py`
- `docs/api/frontend-v2.md`
- `docs/api/changelog.md`
