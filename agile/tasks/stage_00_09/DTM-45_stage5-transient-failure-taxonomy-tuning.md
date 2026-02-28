# DTM-45: TSK-048 Stage 5 transient failure taxonomy tuning for Telegram retries

## Context
- Current reminder retry classifier uses broad exception classes and a short name-based fallback.
- This can misclassify Telegram/API errors and lead to wrong retry decisions.
- Stage 5 follow-up requires refined transient/permanent taxonomy plus better retry observability.

## Goal
- Refine reminder send error taxonomy and retry classifier in `core/reminder.py`.
- Preserve bounded retry/backoff behavior while reducing false retry/no-retry cases.
- Extend smoke coverage for new taxonomy branches.

## Non-goals
- No changes to OpenAI enhancer flow.
- No new external queue/worker infrastructure.
- No production alert policy changes in this task.

## Plan
1. Add explicit send-error classification helper (transient/permanent buckets with labels).
2. Use taxonomy in retry decision and structured send error counters.
3. Extend retry smoke checks with representative Telegram-like error types.
4. Sync docs/sprint/context and Jira evidence.

## Checklist (DoD)
- [x] Retry classifier updated with explicit taxonomy and safe fallback.
- [x] Delivery counters include taxonomy-level observability.
- [x] Smoke checks pass (`py_compile`, retry smoke, reminders-only mock dry-run).
- [x] Jira and sprint/context docs synchronized.

## Work log
- 2026-02-27: Jira `DTM-45` created and moved to `V rabote`; start evidence comment added.
- 2026-02-27: Freshness check started for `core/reminder.py` retry path and `agent/reminder_retry_backoff_smoke.py`.
- 2026-02-27: Implemented explicit send-error taxonomy classifier in reminder delivery (`timeout/network/rate-limit/http/message/unknown`).
- 2026-02-27: Added taxonomy counters (`send_error_transient`, `send_error_permanent`, `send_error_unknown`) and exposed them in quality summary.
- 2026-02-27: Extended retry smoke with rate-limit-name, permanent-message, and unknown-error branches.
- 2026-02-27: Smoke checks passed: `py_compile`, `agent/reminder_retry_backoff_smoke.py`, `local_run.py --mode reminders-only --dry-run --mock-external`.

## Links
- Jira: DTM-45
- Files: core/reminder.py, core/planner.py, agent/reminder_retry_backoff_smoke.py
