# DTM-30 - Stage 3 close-out coverage: manager adapter smoke assertions

## Context
- Stage 3 adapter extraction is completed for active managers (`TaskManager`, `CalendarManager`, `TaskCalendarManager`).
- Existing `agent/render_adapter_smoke.py` validates adapter method call shape, but not manager-level wiring.
- Jira issue: `DTM-30` (status: `V rabote`).

## Goal
- Extend smoke harness to assert manager-level adapter usage for active rendering flows.
- Capture clear evidence that active managers queue writes through adapter API in dry-run safe checks.

## Non-goals
- No feature changes in rendering output.
- No migration/removal of `TaskCalendarManagerOld` in this slice.
- No new test framework bootstrap.

## Plan
1. Extend `agent/render_adapter_smoke.py` with fake repository/sheet fixtures.
2. Add assertions for `TaskManager` and `CalendarManager` adapter-path writes.
3. Run smoke checks (`py_compile`, harness, sync-only dry-run).
4. Sync Jira/sprint/context/backlog docs.

## Checklist (DoD)
- [x] Manager-level adapter assertions added to harness.
- [x] Harness passes locally.
- [x] Relevant smoke checks pass.
- [x] Jira/sprint/docs synchronized.

## Work log
- 2026-02-27: Task created in Jira (`DTM-30`) and moved to `V rabote`.
- 2026-02-27: Extended `agent/render_adapter_smoke.py` with manager-level adapter-path assertions for `TaskManager` and `CalendarManager` using fake renderer/repository fixtures.
- 2026-02-27: Smoke passed: `python -m py_compile agent/render_adapter_smoke.py core/manager.py core/bootstrap.py core/sheet_renderer.py core/adapters.py core/render_contracts.py`, `.venv\\Scripts\\python.exe agent/render_adapter_smoke.py`, `.venv\\Scripts\\python.exe local_run.py --mode sync-only --dry-run`.

## Links
- `agent/render_adapter_smoke.py`
- `core/manager.py`
- `core/use_cases.py`
- `agile/sprint_current.md`
