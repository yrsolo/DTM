# DTM-31 - Stage 3 close-out: TaskCalendarManagerOld legacy path disposition

## Context
- Active planner flow uses `TaskCalendarManager` adapter-based path.
- `TaskCalendarManagerOld` and global helper `write_cur_time` remain in `core/manager.py` as legacy dead branch.
- Jira issue: `DTM-31` (status: `V rabote`).

## Goal
- Remove unused legacy rendering branch to reduce maintenance risk and avoid accidental direct-service path reuse.
- Keep active runtime behavior unchanged.

## Non-goals
- No changes to active render output logic.
- No Stage 4 reminder refactor in this slice.
- No test framework redesign.

## Plan
1. Remove `TaskCalendarManagerOld` and obsolete global helper `write_cur_time`.
2. Ensure no active call-sites rely on removed symbols.
3. Run smoke checks (`py_compile`, adapter smoke, sync-only dry-run).
4. Sync Jira/sprint/context/backlog docs.

## Checklist (DoD)
- [x] Legacy class removed from active module.
- [x] No runtime reference regressions.
- [x] Smoke checks pass.
- [x] Jira/sprint/docs synchronized.

## Work log
- 2026-02-27: Task created in Jira (`DTM-31`) and moved to `V rabote`.
- 2026-02-27: Removed `TaskCalendarManagerOld` and obsolete global helper `write_cur_time` from `core/manager.py`.
- 2026-02-27: Verified no active references remain via `rg` (`TaskCalendarManagerOld`/legacy helper symbols absent in runtime paths).
- 2026-02-27: Smoke passed: `python -m py_compile core/manager.py core/bootstrap.py core/planner.py core/sheet_renderer.py core/adapters.py core/render_contracts.py agent/render_adapter_smoke.py`, `.venv\\Scripts\\python.exe agent/render_adapter_smoke.py`, `.venv\\Scripts\\python.exe local_run.py --mode sync-only --dry-run`.

## Links
- `core/manager.py`
- `core/planner.py`
- `core/use_cases.py`
- `agile/sprint_current.md`
