# DTM-24 - Stage 3 task-calendar renderer alignment

## Context
- `DTM-23` introduced shared render contract scaffold (`core/render_contracts.py`) and integrated it into core `TaskCalendarManager` payload creation path.
- Remaining renderer flow still mixes style/formatting decisions inline with drawing loops in `core/manager.py`.
- Jira issue: `DTM-24` (status: `V rabote`).

## Goal
- Align task-calendar renderer logic to shared render contract usage with cleaner, testable boundaries.
- Keep output parity with existing sheet rendering behavior.

## Non-goals
- No user-visible redesign of sheets.
- No full extraction of all renderers to separate modules in this slice.
- No contract changes for reminder pipeline.

## Plan
1. Identify remaining ad-hoc payload/style branches in task-calendar renderer path.
2. Normalize repeated rendering decisions into helper methods around shared contract.
3. Execute parity smoke checks in dry-run mode and confirm no regressions in flow.
4. Update sprint/docs/Jira evidence.

## Checklist (DoD)
- [ ] Remaining task-calendar render payload branches aligned with shared contract helpers.
- [ ] Existing runtime behavior preserved (dry-run output path unchanged at flow level).
- [ ] Smoke checks pass (`py_compile`, `local_run.py --mode sync-only --dry-run`).
- [ ] `agile/sprint_current.md` updated.
- [ ] Jira evidence comment added and issue transitioned according to lifecycle.

## Work log
- 2026-02-27: Task moved to `V rabote` after `DTM-23` completion.

## Links
- `core/manager.py`
- `core/render_contracts.py`
- `agile/sprint_current.md`
- `doc/03_reconstruction_backlog.md`
