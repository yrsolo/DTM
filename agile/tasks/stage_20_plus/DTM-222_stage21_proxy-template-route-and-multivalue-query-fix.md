# DTM-222: Stage 21 proxy-template route and multi-value query fix

## Context
- Real cloud event log showed:
  - `path='/{proxy+}'`
  - real route in `params.proxy` / `pathParams.proxy`
  - query values in `multiValueQueryStringParameters` / `multiValueParams`.
- Existing route extraction did not prioritize these fields, causing frontend API branch miss and fallback noop.

## Goal
- Resolve frontend API route correctly when gateway sends proxy template path.
- Resolve query params from multi-value and URL/raw query variants.

## Non-goals
- No planner trigger policy changes.
- No API contract changes.

## Plan
1. Prioritize `pathParams.proxy` / `params.proxy` over templated path.
2. Normalize and ignore template `/{proxy+}` as final path.
3. Parse query from `queryStringParameters`, `rawQueryString`, `multiValueQueryStringParameters`, URL, and `multiValueParams`.
4. Verify on synthetic event matching cloud debug payload.

## Checklist (DoD)
- [x] Proxy template route extraction fixed.
- [x] Multi-value query extraction fixed.
- [x] Local smoke on event matching cloud debug shape returns `dtm_frontend_api_payload` (not noop).
- [ ] Cloud test domain verification after deploy.

## Work log
- 2026-03-02: Updated `_http_path` to prioritize `pathParams.proxy` / `params.proxy`.
- 2026-03-02: Updated `_query_params` to support `multiValueQueryStringParameters`, `multiValueParams.queryString`, URL query parsing.
- 2026-03-02: Local smoke on real-shape event returned `200` + `dtm_frontend_api_payload`.

## Links
- `index.py`
