# DTM-9: Stage 1 timing/null input normalization and parser hardening

## Context
- Stage 1 continues data contract stabilization in `core/repository.py`.
- `TimingParser.parse` had a nullable check that could fail on non-scalar payloads.
- `Task` accepted raw mixed types from DataFrame rows without uniform text normalization.

## Goal
- Make timing parsing resilient for `None`/NaN/empty/non-string input payloads.
- Normalize nullable task text fields to predictable values and avoid malformed-data crashes.

## Non-goals
- No refactor of manager/calendar layers.
- No changes to reminder logic or Telegram delivery behavior.

## Mode
- Execution mode

## Plan
1) Harden null detection in parser path with safe helper for mixed payloads.
2) Normalize task text fields in one place before timing parsing.
3) Run smoke-check, update docs, and close Jira lifecycle with evidence.

## Checklist (DoD)
- [x] `TimingParser.parse` safely handles null/empty/non-string values.
- [x] `Task` fields are null-safe normalized before downstream usage.
- [x] Smoke-check passes (`py_compile`, local launcher help, dry-run sync mode).
- [x] Jira lifecycle/comments updated with concrete execution evidence.

## Work log
- 2026-02-27: Jira issue DTM-9 created; status confirmed as `В работе` before code changes.
- 2026-02-27: Added `_is_nullish` and `_normalize_text` helpers; hardened parser and task field normalization in `core/repository.py`.
- 2026-02-27: Smoke-check passed:
  - `.venv\Scripts\python.exe -m py_compile core\repository.py`
  - `.venv\Scripts\python.exe local_run.py --help`
  - `.venv\Scripts\python.exe local_run.py --mode sync-only --dry-run`
- 2026-02-27: Timer-equivalent safe run passed:
  - `.venv\Scripts\python.exe local_run.py --mode timer --dry-run`
- 2026-02-27: Jira evidence comment added; issue transitioned to `Gotovo`.

## Links
- Jira: DTM-9
- Notes: doc/03_reconstruction_backlog.md (Stage 1)
