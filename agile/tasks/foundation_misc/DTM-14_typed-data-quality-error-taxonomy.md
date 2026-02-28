# DTM-14: Stage 1 typed data-quality error taxonomy and reporting

## Context
- Stage 1 already has typed row contracts and schema guardrails, but failures still raise generic `ValueError`.
- Diagnostics for task/people input quality should be unified before moving to row-level validation policy.

## Goal
- Introduce typed data-quality exceptions for sheet-loading paths.
- Reuse one reporting format for missing-column failures in tasks/people loaders.
- Keep current fail-fast behavior while improving observability and future extension points.

## Non-goals
- No changes to planner business decisions.
- No changes to Telegram reminder generation/delivery.
- No broad refactor beyond task/people data-loading diagnostics.

## Mode
- Execution mode

## Plan
1) Add typed data-quality exception classes in core domain layer.
2) Replace generic missing-column `ValueError` in repository/people with typed exceptions.
3) Run smoke checks and sync sprint/docs/Jira lifecycle.

## Risks
- Exception class swap can break callers if they catch only `ValueError`.
- Error message drift may affect manual troubleshooting habits.

## Acceptance Criteria
- Missing required task columns raise a typed exception with sheet context.
- Missing required people columns raise a typed exception with sheet context.
- Existing dry-run runtime commands stay green.

## Checklist (DoD)
- [x] Typed error taxonomy added and used in task/people schema checks.
- [x] Error messages include spreadsheet/sheet context and missing column names.
- [x] Smoke checks passed.
- [x] Jira evidence comment + status `Gotovo`.
- [x] Sprint/docs synced with final state.

## Work log
- 2026-02-27: Jira issue DTM-14 created and moved to `V rabote`; start evidence comment added.
- 2026-02-27: Pre-task freshness/trust check completed in `agile/context_registry.md`.
- 2026-02-27: Added `core/errors.py` with `DataQualityError` and `MissingRequiredColumnsError`.
- 2026-02-27: Switched missing-header checks in `core/repository.py` and `core/people.py` from generic `ValueError` to `MissingRequiredColumnsError`.
- 2026-02-27: Smoke checks passed:
  - `.venv\Scripts\python.exe -m py_compile core\errors.py core\repository.py core\people.py core\contracts.py`
  - `.venv\Scripts\python.exe local_run.py --mode timer --dry-run`
  - `.venv\Scripts\python.exe local_run.py --mode reminders-only --dry-run`
- 2026-02-27: Jira evidence comment added; issue transitioned to done category (`Gotovo`).

## Links
- Jira: DTM-14
- Sprint: agile/sprint_current.md
