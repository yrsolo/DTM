# DTM-5: Add run modes `sync-only` / `reminders-only` and `--dry-run`

## Context
- Stage 0 backlog requires safer execution control for local verification.
- Current launcher supports `timer`, `morning`, `test`, but no explicit dry-run write protection.

## Goal
- Add explicit execution modes:
  - `sync-only` (no reminders),
  - `reminders-only` (no sheet updates),
  - `--dry-run` (no write calls to Google API).

## Non-goals
- No change to business semantics of existing `timer/morning/test`.
- No production deployment changes.

## Mode
- Execution mode

## Plan
1) Extend CLI and main orchestration mode mapping.
2) Thread dry-run flag through planner/manager/service write paths.
3) Add smoke-check commands and update docs.

## Checklist (DoD)
- [x] New modes available from local launcher.
- [x] Dry-run prevents write operations while preserving readable diff/log output.
- [x] Existing modes remain backward compatible.
- [x] Docs updated (`README`, relevant `doc/*`).
- [x] Jira status/comments updated with evidence.

## Work log
- 2026-02-27: Task prepared by TeamLead for next sequential execution block.
- 2026-02-27: Pre-task freshness check completed (`local_run.py`, `main.py`, `git log`, `git blame`).
- 2026-02-27: Task moved to blocked in local sprint board because Jira control plane is unavailable in shell (`JIRA_*` env vars missing); owner escalation sent via `agent/notify_owner.py`.
- 2026-02-27: Jira access validated from `.env` (`/rest/api/3/myself` = 200), issue moved to `В работе`.
- 2026-02-27: Implemented `sync-only` / `reminders-only` modes and `--dry-run` with write no-op guard in Google Sheets service.
- 2026-02-27: Smoke-check passed:
  - `.venv\Scripts\python.exe local_run.py --help`
  - `.venv\Scripts\python.exe local_run.py --mode sync-only --dry-run`

## Links
- Jira: DTM-5
- Notes: doc/03_reconstruction_backlog.md (section 0.3)
