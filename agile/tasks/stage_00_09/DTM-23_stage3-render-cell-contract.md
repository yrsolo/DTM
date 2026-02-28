# DTM-23 - Stage 3 calendar rendering shared cell-contract scaffold

## Context
- Stage 2 isolated domain/application/infrastructure boundaries; Stage 3 starts rendering refactor with minimal risk slices.
- `core/manager.py` still builds many ad-hoc `cell_data` dict payloads directly in render flow.
- Jira issue: `DTM-23` (status: `Gotovo`).

## Goal
- Introduce a shared, typed render cell contract scaffold.
- Apply scaffold to active task-calendar rendering path without behavior changes.
- Keep changes reversible and small to unblock next Stage 3 slices (`DTM-24`, `DTM-25`).

## Non-goals
- No visual/formatting behavior changes in sheets output.
- No large module split of all manager classes in this slice.
- No Google API adapter rewrite.

## Plan
1. Add render contract module with typed payload object(s) for sheet cell updates.
2. Refactor `TaskCalendarManager` cell payload construction to use shared contract.
3. Run smoke checks for compile + safe runtime dry-run modes.
4. Sync sprint/task/docs and Jira lifecycle evidence.

## Checklist (DoD)
- [x] Shared render contract module added.
- [x] `TaskCalendarManager` uses shared contract for cell payload generation.
- [x] Smoke checks pass (`py_compile`, `local_run.py --mode sync-only --dry-run`).
- [x] `agile/sprint_current.md` updated.
- [x] `agile/context_registry.md` updated with trust evidence.
- [x] Jira evidence comment added and issue moved to `Gotovo`.

## Work log
- 2026-02-27: Task started; Jira `DTM-23` moved to `V rabote`.
- 2026-02-27: Freshness check run on `core/manager.py` hotspots using `git log`, `git blame`, and code scan.
- 2026-02-27: Added shared `RenderCell` contract (`core/render_contracts.py`) and migrated `TaskCalendarManager` payload creation to contract-based assembly.
- 2026-02-27: Smoke passed: `python -m py_compile core/render_contracts.py core/manager.py`, `python local_run.py --mode sync-only --dry-run`.
- 2026-02-27: Jira evidence comment added; issue transitioned to `Gotovo`.

## Links
- `core/manager.py`
- `agile/sprint_current.md`
- `agile/context_registry.md`
- `doc/03_reconstruction_backlog.md`
