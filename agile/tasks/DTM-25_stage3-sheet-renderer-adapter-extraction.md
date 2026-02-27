# DTM-25 - Stage 3 sheet renderer adapter extraction

## Context
- `DTM-23` introduced shared render cell contract.
- `DTM-24` aligned task-calendar renderer payload construction around reusable helper methods.
- Rendering writes are still owned directly by manager classes, without dedicated sheet-render adapter object.
- Jira issue: `DTM-25` (status: `V rabote`).

## Goal
- Extract sheet renderer adapter boundary from manager rendering flow.
- Keep manager classes focused on orchestration and data shaping, with rendering writes delegated to adapter methods.

## Non-goals
- No broad rewrite of GoogleSheetsService internals.
- No behavior change in rendered sheets.
- No reminder pipeline changes.

## Plan
1. Define minimal adapter interface for sheet rendering write operations used by calendar/task-calendar managers.
2. Introduce adapter implementation that wraps current service update patterns.
3. Rewire manager rendering paths to use adapter boundary.
4. Run smoke checks and sync lifecycle/docs.

## Checklist (DoD)
- [ ] Sheet renderer adapter boundary introduced and wired.
- [ ] Manager rendering paths use adapter boundary for write operations.
- [ ] Smoke checks pass (`py_compile`, `local_run.py --mode sync-only --dry-run`).
- [ ] `agile/sprint_current.md` and relevant docs updated.
- [ ] Jira evidence comment added and issue transitioned per lifecycle.

## Work log
- 2026-02-27: Task moved to `V rabote` after `DTM-24` completion.

## Links
- `core/manager.py`
- `core/render_contracts.py`
- `core/adapters.py`
- `agile/sprint_current.md`
