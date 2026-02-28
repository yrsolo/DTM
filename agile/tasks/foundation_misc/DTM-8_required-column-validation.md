# DTM-8: Stage 1 required task-column validation in repository

## Context
- Stage 1 starts with data contract stabilization.
- Task loading currently assumes required columns exist and can fail with low-quality diagnostics.

## Goal
- Add explicit validation for required task columns before row mapping.
- Normalize missing optional values safely to reduce avoidable runtime crashes.

## Non-goals
- No full domain model rewrite in this task.
- No reminder pipeline behavior changes.

## Mode
- Execution mode

## Plan
1) Add required-column check in `GoogleSheetsTaskRepository` before task conversion.
2) Use safer row mapping for optional fields to avoid `KeyError` on malformed rows.
3) Update docs + run smoke checks.

## Checklist (DoD)
- [x] Missing required columns produce explicit actionable error.
- [x] Optional field normalization is safe for empty/NaN values.
- [x] Smoke-check passes (import/compile + launcher help).
- [x] Jira lifecycle/comments updated with evidence.

## Work log
- 2026-02-27: Jira issue DTM-8 created and moved to `V rabote`.
- 2026-02-27: Added `_validate_required_columns` in `GoogleSheetsTaskRepository` with explicit error message.
- 2026-02-27: Switched row mapping to safe lookup (`row.get`) for optional/malformed values.
- 2026-02-27: Smoke-check passed:
  - `.venv\Scripts\python.exe -m py_compile core\repository.py`
  - `.venv\Scripts\python.exe local_run.py --help`
- 2026-02-27: Jira evidence comment added; issue transitioned to `Gotovo`.

## Links
- Jira: DTM-8
- Notes: doc/03_reconstruction_backlog.md (Stage 1)
