# DTM-203: Stage 21 API doc HTML page and gateway path matching

## Context
- Owner asked that API docs open as a readable mini-page, not raw technical response.
- `/api/v1/frontend/doc` returned runtime noop in some gateway path forms.

## Goal
- Render human-friendly HTML docs page for API contract.
- Keep JSON contract available by explicit query switch.
- Make route matching resilient to gateway path variants (prefixes/trailing slash).

## Non-goals
- No changes in planner business logic.
- No changes in frontend payload schema.

## Plan
1. Add HTML response helper.
2. Add static HTML doc page builder.
3. Add path normalization and suffix matching for API gateway forms.
4. Keep `?format=json` support for machine-readable doc.

## Checklist (DoD)
- [x] `GET /api/v1/frontend/doc` returns HTML page.
- [x] `GET /api/v1/frontend/doc?format=json` returns JSON contract.
- [x] Gateway path variants still resolve endpoints.
- [x] Local smoke checks passed.

## Work log
- 2026-03-02: Updated `index.py` with `_html_response`, `_frontend_api_doc_html`, path normalization/matching helpers.
- 2026-03-02: Added JSON fallback via `format=json`.

## Links
- `index.py`
