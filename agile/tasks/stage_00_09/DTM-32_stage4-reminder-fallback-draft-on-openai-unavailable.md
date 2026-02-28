# DTM-32 - Stage 4 fallback: send draft when OpenAI enhancer unavailable

## Context
- Reminder pipeline builds draft text and then tries OpenAI enhancement.
- Current flow stores enhancer result directly; empty/None enhancer response can leak into delivery path.
- Jira issue: `DTM-32` (status: `V rabote`).

## Goal
- Ensure reminder delivery always falls back to draft message when OpenAI enhancement is unavailable, empty, or invalid.
- Add deterministic local smoke check for fallback behavior without external API calls.

## Non-goals
- No idempotency layer in this slice.
- No message style redesign.
- No external service contract changes.

## Plan
1. Harden fallback in `Reminder.get_enhanced_message` and `Reminder.send_reminders`.
2. Add local fallback smoke script under `agent/`.
3. Run reminder-relevant smoke checks.
4. Sync Jira/sprint/context/backlog docs.

## Checklist (DoD)
- [x] Draft fallback enforced for empty enhancer output.
- [x] Local fallback smoke script passes.
- [x] Reminder dry-run smoke passes.
- [x] Jira/sprint/docs synchronized.

## Work log
- 2026-02-27: Task created in Jira (`DTM-32`) and moved to `V rabote`.
- 2026-02-27: `Reminder.get_enhanced_message` hardened: empty/None enhancer response now falls back to draft.
- 2026-02-27: `Reminder.send_reminders` hardened: empty message falls back to saved draft (or is safely skipped if no draft exists).
- 2026-02-27: Added deterministic fallback smoke script `agent/reminder_fallback_smoke.py` (no external API calls).
- 2026-02-27: Smoke passed: `python -m py_compile core/reminder.py core/bootstrap.py core/use_cases.py agent/reminder_fallback_smoke.py`, `.venv\\Scripts\\python.exe agent/reminder_fallback_smoke.py`, `.venv\\Scripts\\python.exe local_run.py --mode reminders-only --dry-run --mock-external`.

## Links
- `core/reminder.py`
- `core/bootstrap.py`
- `core/use_cases.py`
- `agile/sprint_current.md`
