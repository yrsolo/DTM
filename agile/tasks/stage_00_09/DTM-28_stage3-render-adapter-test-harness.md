# DTM-28 - Stage 3 render adapter test harness (dry-run request assertions)

## Context
- `DTM-26` and `DTM-27` moved calendar/task-calendar rendering to adapter and render-contract boundaries.
- Repository has no standardized pytest/unittest suite yet.
- Jira issue: `DTM-28` (status: `Gotovo`).

## Goal
- Add a lightweight executable test-harness for render adapter integration assertions.
- Validate adapter call-shape and spreadsheet/sheet scoping in a deterministic local script.

## Non-goals
- No full test framework bootstrap in this slice.
- No network/real Google API calls.
- No behavior redesign in render managers.

## Plan
1. Add a fake-service based smoke script for `ServiceSheetRenderAdapter`.
2. Assert call sequence and key payload/scoping invariants.
3. Run harness and keep regular sync dry-run smoke green.
4. Sync Jira/sprint/docs lifecycle.

## Checklist (DoD)
- [x] Adapter test-harness script added.
- [x] Harness passes locally with deterministic assertions.
- [x] Relevant smoke checks pass.
- [x] Jira/sprint/docs synchronized.

## Work log
- 2026-02-27: Task moved to `V rabote` after `DTM-27` completion.
- 2026-02-27: Added `agent/render_adapter_smoke.py` with fake-service assertions for adapter call sequence and scoping.
- 2026-02-27: Smoke passed: `python -m py_compile core/manager.py core/bootstrap.py core/sheet_renderer.py core/adapters.py agent/render_adapter_smoke.py`, `python agent/render_adapter_smoke.py`, `python local_run.py --mode sync-only --dry-run`.
- 2026-02-27: Jira evidence comment added; issue transitioned to `Gotovo`.

## Links
- `core/sheet_renderer.py`
- `core/adapters.py`
- `agent/render_adapter_smoke.py`
- `agile/sprint_current.md`
