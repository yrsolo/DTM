# DTM-33 - Stage 4 idempotency: prevent duplicate reminder sends in same run

## Context
- Reminder pipeline currently sends messages from `enhanced_messages` without duplicate-delivery tracking.
- Repeated invocation of `send_reminders` in the same runtime may duplicate outbound Telegram sends.
- Jira issue: `DTM-33` (status: `V rabote`).

## Goal
- Add in-run idempotent delivery guard for reminder sends.
- Provide deterministic smoke proving duplicate prevention.

## Non-goals
- No persistent cross-run dedup storage.
- No scheduler redesign.
- No changes to reminder message content.

## Plan
1. Add delivery-key guard set in `Reminder`.
2. Skip duplicate sends in `send_reminders` when key already delivered.
3. Add deterministic local smoke for duplicate guard behavior.
4. Run reminder smoke + sync Jira/sprint/docs.

## Checklist (DoD)
- [x] Duplicate send guard added and wired.
- [x] Idempotency smoke passes.
- [x] Reminder dry-run smoke passes.
- [x] Jira/sprint/docs synchronized.

## Work log
- 2026-02-27: Task created in Jira (`DTM-33`) and moved to `V rabote`.
- 2026-02-27: Added in-run delivery key guard (`sent_delivery_keys`) and duplicate skip logic in `Reminder.send_reminders`.
- 2026-02-27: Added `_build_delivery_key(...)` using day/designer/chat/message hash for deterministic dedup keying.
- 2026-02-27: Added deterministic smoke script `agent/reminder_idempotency_smoke.py` validating duplicate-send prevention on repeated `send_reminders` calls.
- 2026-02-27: Smoke passed: `python -m py_compile core/reminder.py agent/reminder_idempotency_smoke.py agent/reminder_fallback_smoke.py core/bootstrap.py core/use_cases.py`, `.venv\\Scripts\\python.exe agent/reminder_idempotency_smoke.py`, `.venv\\Scripts\\python.exe local_run.py --mode reminders-only --dry-run --mock-external`.

## Links
- `core/reminder.py`
- `core/use_cases.py`
- `agile/sprint_current.md`
