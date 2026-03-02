# DTM-218: Stage 21 API HTTP method fallback hotfix

## Context
- Test API domain returned `dtm_runtime_noop` for frontend endpoints.
- Root cause: some HTTP gateway event shapes do not include method where current parser expected it.

## Goal
- Make HTTP method extraction robust for multiple event layouts.
- Ensure frontend API endpoint still treats missing method in HTTP event as read-only `GET`.

## Non-goals
- No changes to planner trigger gate behavior for non-API HTTP calls.

## Plan
1. Expand `_http_method` parsing in `index.py`.
2. Add fallback to `GET` in frontend API handler when event is HTTP and method is missing.
3. Run local smoke for doc/data endpoint shapes.

## Checklist (DoD)
- [x] Method parser handles `requestContext.http.method`, `requestContext.httpMethod`, top-level `httpMethod/method/requestMethod`.
- [x] Missing method no longer forces noop for frontend API requests.
- [x] Local smoke confirms `/api/v1/frontend/doc` and `/api/v1/frontend` responses are API/doc artifacts.

## Work log
- 2026-03-02: Updated method extraction and fallback behavior in `index.py`.
- 2026-03-02: Ran local smoke via `.venv` for doc endpoint and patched data endpoint shape; both returned API artifacts with `200`.

## Links
- `index.py`
