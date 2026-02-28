# DTM-13: Stage 1 schema guardrails for task/people row contracts

## Context
- Stage 1 now has typed row contracts (`core/contracts.py`), but explicit schema guardrails should be centralized there.
- Task required-column validation exists in repository; people sheet still lacks explicit required-header fail-fast.

## Goal
- Add explicit required-header metadata to row contracts.
- Use that metadata for fail-fast validation in task and people loaders with actionable errors.

## Non-goals
- No behavior change in downstream business logic.
- No reminder text/delivery changes.

## Mode
- Execution mode

## Plan
1) Extend contracts with required-column helpers.
2) Route repository and people schema checks through contracts.
3) Run smoke checks + sync Jira/docs.

## Checklist (DoD)
- [x] Task and people required columns are derived from typed contracts.
- [x] Missing headers raise explicit ValueError with sheet context.
- [x] Smoke checks passed.
- [x] Jira evidence comment + status `Gotovo`.

## Work log
- 2026-02-27: Jira issue DTM-13 created and moved to `V rabote`.
- 2026-02-27: Added contract-level required-column metadata methods:
  - `TaskRowContract.required_columns(...)`
  - `PersonRowContract.required_columns(...)`
- 2026-02-27: Wired schema checks through contracts:
  - `core/repository.py::_validate_required_columns` uses `TaskRowContract.required_columns`.
  - `core/people.py` now has explicit `_validate_required_columns` with sheet-context error.
- 2026-02-27: Smoke checks passed:
  - `.venv\Scripts\python.exe -m py_compile core\contracts.py core\repository.py core\people.py`
  - `.venv\Scripts\python.exe local_run.py --help`
  - `.venv\Scripts\python.exe local_run.py --mode timer --dry-run`
  - `.venv\Scripts\python.exe local_run.py --mode reminders-only --dry-run`
- 2026-02-27: Jira evidence comment added; issue transitioned to `Gotovo`.

## Links
- Jira: DTM-13
- Notes: doc/03_reconstruction_backlog.md
