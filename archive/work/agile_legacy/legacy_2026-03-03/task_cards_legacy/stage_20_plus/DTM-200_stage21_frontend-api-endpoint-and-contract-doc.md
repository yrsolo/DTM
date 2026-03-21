# DTM-200: Stage 21 frontend API endpoint and contract doc

## Context
- Owner requested that API starts returning frontend data and includes clear request/response format reference.

## Goal
- Add HTTP `GET` endpoint(s) in cloud handler returning stable JSON for frontend.
- Publish human-readable API contract document.

## Non-goals
- No migration of existing planner flow.
- No visual frontend implementation changes.

## Plan
1. Add payload builder for frontend data serialization.
2. Add route handling in cloud `index.py`.
3. Publish API contract doc and update README/docs.

## Checklist (DoD)
- [x] Endpoint `GET /api/v1/frontend` implemented.
- [x] Alias endpoint `GET /api/v1/read-model` implemented.
- [x] Doc endpoint `GET /api/v1/frontend/doc` implemented.
- [x] Contract doc published.
- [x] Docs updated.

## Work log
- 2026-03-02: Added `core/api_payload.py` serializer with task/deadline/people payload.
- 2026-03-02: Added HTTP route handling in `index.py`.
- 2026-03-02: Added `doc/ops/frontend_api_contract.md` and updated README/module docs.

## Links
- `index.py`
- `core/api_payload.py`
- `doc/ops/frontend_api_contract.md`
- `README.md`
