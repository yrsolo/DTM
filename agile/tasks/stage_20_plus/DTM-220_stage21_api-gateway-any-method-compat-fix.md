# DTM-220: Stage 21 API Gateway ANY method compatibility fix

## Context
- Test API domain still returned `dtm_runtime_noop` after previous method parser fix.
- Yandex API Gateway with `x-yc-apigateway-any-method` may pass `method=ANY`.
- Frontend API handler accepted only `GET`, causing false route miss and fallback noop.

## Goal
- Treat `ANY` as `GET` for frontend read-only API endpoints.

## Non-goals
- No planner mode trigger changes.
- No POST/PUT behavior expansion.

## Plan
1. Add `ANY -> GET` normalization in frontend API route branch.
2. Run local smoke with event payload containing `requestContext.http.method=ANY`.

## Checklist (DoD)
- [x] Route compatibility for `method=ANY` implemented.
- [x] Local smoke for `/api/v1/frontend/doc` with `ANY` returns HTML API doc response.
- [ ] Cloud test domain verification after deploy.

## Work log
- 2026-03-02: Added `ANY -> GET` normalization in `index.py`.
- 2026-03-02: Local smoke via `.venv` confirmed `200 text/html` for doc endpoint with `method=ANY`.

## Links
- `index.py`
- `agile/tasks/stage_20_plus/DTM-219_stage21_test-deploy-verification-blocked-by-github-token-scope.md`
