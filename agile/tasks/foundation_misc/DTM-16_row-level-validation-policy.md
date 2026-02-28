# DTM-16: Stage 1 row-level validation policy for malformed task/person rows

## Context
- Stage 1 has header-level validation and typed contracts, but malformed row values can still crash loading paths.
- Current loaders (`core/repository.py`, `core/people.py`) do not provide explicit row-level fail-soft policy.

## Goal
- Define and implement row-level validation policy with non-fatal skip for malformed rows.
- Keep pipeline running while collecting diagnostics for skipped rows.

## Non-goals
- No changes to business scheduling rules.
- No reminder text or delivery behavior changes.

## Mode
- Execution mode

## Plan
1) Add reusable row-issue diagnostic model.
2) Implement task/person row-level guards with skip policy for malformed rows.
3) Run smoke checks and sync Jira/docs/sprint.

## Risks
- Overly broad skipping could hide logic bugs.
- New validation rules can drop rows unexpectedly if too strict.

## Acceptance Criteria
- Malformed rows do not stop full task/people loading.
- Skipped rows are recorded with row context and reason.
- Existing dry-run flows remain green.

## Checklist (DoD)
- [x] Row-level issue model added.
- [x] Task loader applies malformed-row fail-soft policy.
- [x] People loader applies malformed-row fail-soft policy.
- [x] Smoke checks passed.
- [x] Jira evidence comment + status `Gotovo`.

## Work log
- 2026-02-27: Jira issue DTM-16 created and moved to `V rabote`.
- 2026-02-27: Pre-task freshness check performed via git log/blame on `core/repository.py` and `core/people.py`.
- 2026-02-27: Added `RowValidationIssue` model in `core/errors.py`.
- 2026-02-27: Added row-level fail-soft and diagnostics (`row_issues`) in task/people loaders:
  - skip malformed mapping rows;
  - skip missing IDs;
  - skip duplicate IDs.
- 2026-02-27: Smoke checks passed:
  - `.venv\Scripts\python.exe -m py_compile core\errors.py core\repository.py core\people.py core\contracts.py`
  - `.venv\Scripts\python.exe local_run.py --mode timer --dry-run`
  - `.venv\Scripts\python.exe local_run.py --mode reminders-only --dry-run`
  - targeted row-policy smoke script (`row_policy_smoke_ok`)
- 2026-02-27: Jira evidence comment added and issue moved to done category (`Gotovo`).

## Links
- Jira: DTM-16
- Sprint: agile/sprint_current.md
