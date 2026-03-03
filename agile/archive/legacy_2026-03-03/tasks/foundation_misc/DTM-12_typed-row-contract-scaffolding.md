# DTM-12: Stage 1 typed Task/Person row-contract scaffolding

## Context
- Stage 1 requires explicit and safer data contracts for incoming sheet rows.
- Current row mapping logic in `core/repository.py` and `core/people.py` is functional but scattered.

## Goal
- Introduce typed, non-breaking row-contract objects for task/person mapping.
- Keep runtime behavior unchanged while improving contract clarity.

## Non-goals
- No domain-layer rewrite.
- No behavior changes in reminder delivery or calendar rendering.

## Mode
- Execution mode

## Plan
1) Add typed row-contract module with null-safe normalization helpers.
2) Route task/person row mapping through typed contracts.
3) Run smoke checks and sync docs/Jira lifecycle.

## Checklist (DoD)
- [x] Typed Task/Person row-contract classes added.
- [x] Repository/people mapping switched to typed contracts without behavior regression.
- [x] Smoke checks passed.
- [x] Jira evidence comment + status `Gotovo`.

## Work log
- 2026-02-27: Jira issue DTM-12 created and moved to `V rabote`.
- 2026-02-27: Added `core/contracts.py` with `TaskRowContract` and `PersonRowContract`, plus shared null-safe normalization helpers.
- 2026-02-27: Switched row mapping to typed contracts:
  - `core/repository.py` now builds `Task` via `TaskRowContract`.
  - `core/people.py` now builds `Person`/`Designer` via `PersonRowContract`.
- 2026-02-27: Smoke checks passed:
  - `.venv\Scripts\python.exe -m py_compile core\contracts.py core\repository.py core\people.py`
  - `.venv\Scripts\python.exe local_run.py --help`
  - `.venv\Scripts\python.exe local_run.py --mode timer --dry-run`
  - `.venv\Scripts\python.exe local_run.py --mode reminders-only --dry-run`
- 2026-02-27: Jira evidence comment added; issue transitioned to `Gotovo`.

## Links
- Jira: DTM-12
- Notes: doc/03_reconstruction_backlog.md
