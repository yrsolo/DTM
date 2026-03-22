# CAM-2026-03-22-ACTIVE-DOCS-RUNTIME-DRIFT-FIX-V1

## Why

Active docs still pointed at deleted handler-era paths such as `frontend_v2_handler.py` and `src/services/timer_pipeline.py`, even though the runnable runtime had already moved to the current browser-read service split and `platform/runtime`.

## Goal

Make active docs describe the current runtime seams truthfully:
- primary browser read goes through `access_api` application/browser-read seams
- snapshot update goes through `src/platform/runtime/timer_pipeline.py` and `snapshot.module`
- attachment docs point at current APIs/services rather than removed handler-era files

## Trust

- source: current runnable code in `src/contexts/access_api/**`, `src/contexts/snapshot/**`, `src/platform/runtime/timer_pipeline.py`, `src/entrypoints/http/router.py`
- last_verified_at: 2026-03-22
- verified_by: Codex
- evidence:
  - direct code reads of current router/module/service files
  - repo grep for stale `frontend_v2_handler.py` / `src/services/timer_pipeline.py` references
- trust_level: high
- notes: code, not prior docs, was treated as the authority for this wave

## Tasks

1. Update active runtime docs to current browser-read and timer/snapshot seams.
2. Update active attachment integration docs to current read/mutation code pointers.
3. Verify active docs no longer reference removed handler-era paths or retired service roots.
