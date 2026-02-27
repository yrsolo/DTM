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
- [ ] New modes available from local launcher.
- [ ] Dry-run prevents write operations while preserving readable diff/log output.
- [ ] Existing modes remain backward compatible.
- [ ] Docs updated (`README`, relevant `doc/*`).
- [ ] Jira status/comments updated with evidence.

## Work log
- 2026-02-27: Task prepared by TeamLead for next sequential execution block.

## Links
- Jira: DTM-5
- Notes: doc/03_reconstruction_backlog.md (section 0.3)
