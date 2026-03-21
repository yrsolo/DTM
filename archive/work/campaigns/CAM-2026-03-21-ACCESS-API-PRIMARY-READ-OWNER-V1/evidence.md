# CAM-2026-03-21-ACCESS-API-PRIMARY-READ-OWNER-V1 Evidence

## Trust Gate

- source: current active browser read path
  - last_verified_at: `2026-03-21`
  - verified_by: `Codex`
  - evidence:
    - `src/entrypoints/http/router.py`
    - `src/contexts/access_api/public.py`
    - `src/contexts/access_api/module.py`
    - `src/contexts/access_api/internal/browser_routes.py`
    - `src/contexts/access_api/internal/frontend_v2_handler.py`
    - `tests/api/test_frontend_api_routing.py`
    - `tests/api/test_info_observability.py`
    - `tests/api/test_task_attachment_read_handler.py`
  - trust_level: `high`
  - notes: current code confirms the residual smell is real; `access_api` still presents the primary browser read path through handler-catalog grammar.

## Active Tasks

- [x] verify the current smell against active code
- [x] replace public/module handler-catalog grammar with scenario-owned browser read surface
- [x] align router and tests
- [x] record closeout verdict

## Closeout

- before: `access_api` was read through `get_*_handler` functions and a `browser_routes` bundle that still made the primary browser read side feel transport-shaped.
- after: `access_api` now exposes one browser-read entry, `HttpRouter` talks to that one entry, and the owning entry lives in `access_api.application` rather than under `internal`.
- verification:
  - `python -m unittest tests.api.test_frontend_api_routing tests.api.test_info_observability tests.api.test_task_attachment_read_handler tests.entrypoint.test_handler tests.architecture.test_guardrails_v0 tests.entrypoints.test_import_safety -v`
  - `rg -n "frontend_root_handler|frontend_v2_handler|info_handler|people_snapshot_handler|task_attachment_read_handler|BrowserRoutesHandler|FrontendRootHandler|FrontendV2Handler|InfoHandler|PeopleSnapshotHandler|TaskAttachmentReadHandler|get_browser_routes_handler|get_frontend_v2_handler|get_info_handler|get_people_snapshot_handler|get_task_attachment_read_handler" src tests`
- next worst smell: `attachments` still exposed its scenario through public `get_*_job` grammar.
