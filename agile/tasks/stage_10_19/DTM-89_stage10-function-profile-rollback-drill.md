# DTM-89: Stage 10 function profile rollback drill and recovery notes

## Context
- Stage 10 requires operational hardening, including explicit rollback procedure for cloud function profile.
- Existing docs describe deploy and smoke checks, but no concise rollback drill exists.

## Goal
- Publish rollback drill and recovery-note template for fast incident response.

## Non-goals
- No automated rollback implementation in this task.
- No runtime code changes.

## Plan
1. Define rollback trigger conditions.
2. Publish step-by-step rollback drill.
3. Add recovery-note template and prevention checklist.
4. Record Jira evidence and update sprint/backlog counters.

## Checklist (DoD)
- [x] Jira key exists (`DTM-89`) and moved to `В работе`.
- [x] Rollback drill doc published in `doc/ops`.
- [x] Jira evidence comment added.
- [x] Jira moved to `Готово`.
- [x] Telegram completion sent.

## Work log
- 2026-02-27: Created Jira issue `DTM-89`, moved to `В работе`.
- 2026-02-27: Published rollback drill document with trigger conditions, steps, and recovery template.
- 2026-02-27: Jira evidence comment added; moved to `Готово`; owner completion notification sent via Telegram.

## Links
- Jira: DTM-89
- File: `doc/ops/stage10_function_rollback_drill.md`
