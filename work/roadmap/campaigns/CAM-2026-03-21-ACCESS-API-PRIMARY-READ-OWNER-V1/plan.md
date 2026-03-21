# CAM-2026-03-21-ACCESS-API-PRIMARY-READ-OWNER-V1

## Why

`contexts/access_api` exists, but it still reads mainly as a transport-shaped handler catalog:

- `get_browser_routes_handler`
- `get_frontend_v2_handler`
- `get_info_handler`
- `get_people_snapshot_handler`
- `get_task_attachment_read_handler`

That means the primary browser read-side still feels like a set of HTTP branches, not one owning module-first scenario.

## Smell

`access_api` is still handler-shaped instead of primary-read-model-shaped.

## Target Ideal

The browser-facing read path is read as:

- `contexts.access_api.public`
- `contexts.access_api.module`
- one scenario-owned browser read surface
- internal transport adapters only as details

## Kill Criteria

1. public/module grammar no longer centers on `get_*_handler`
2. the browser read surface is exposed through one scenario-owned access-api entry
3. `HttpRouter` reads `access_api` as one browser read center, not a route-bundle handler catalog
4. existing HTTP behavior and test expectations stay stable

## Scope Boundary

- `src/contexts/access_api/public.py`
- `src/contexts/access_api/module.py`
- `src/contexts/access_api/internal/*` as needed for the first ownership cut
- `src/entrypoints/http/router.py`
- affected tests under `tests/api/*`

## Non-Goals

- no payload/schema changes
- no rewrite of info/people/attachment read internals yet
- no cross-module read-contract redesign in this wave

## Tasks

- [ ] trust-check the current browser read path against code
- [ ] replace handler-catalog public grammar with scenario-owned access-api surface
- [ ] align router/tests to the new owning path
- [ ] record before/after and next worst smell in evidence
