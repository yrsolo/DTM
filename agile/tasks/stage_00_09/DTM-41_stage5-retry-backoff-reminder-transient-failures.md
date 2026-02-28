# DTM-41: TSK-044 Stage 5 retry/backoff policy for reminder transient failures

## Context
- Reminder delivery currently performs single send attempt and increments `send_errors` on failure.
- `R-007` in risk register tracks missing explicit retry/backoff policy for transient Telegram failures.
- Stage 5 follow-up requires controlled retry strategy without breaking idempotency and mock/dry-run behavior.

## Goal
- Implement bounded retry/backoff for transient Telegram send failures in reminder pipeline.
- Keep retries deterministic and observable via delivery counters and smoke checks.

## Non-goals
- No changes to OpenAI enhancement flow.
- No external queue or scheduler integration.

## Plan
1. Add transient error classification and bounded retry/backoff in `core/reminder.py`.
2. Extend delivery counters and quality report summary with retry metrics.
3. Add deterministic smoke for retry success/exhaustion/non-transient failure branches.
4. Sync sprint/context/risk/backlog docs and Jira evidence.

## Checklist (DoD)
- [x] Retry/backoff policy implemented for transient failures only.
- [x] Idempotency behavior remains intact.
- [x] Smoke-checks passing (compile + retry smoke + reminders dry-run).
- [x] Jira/docs/sprint/context synchronized.

## Work log
- 2026-02-27: Jira `DTM-41` created, moved to `В работе`, start evidence comment added.
- 2026-02-27: Implemented bounded transient retry/backoff in `Reminder._deliver_message` with configurable attempts/backoff and deterministic sleep injection for tests.
- 2026-02-27: Added retry counters (`send_retry_attempts`, `send_retry_exhausted`) to reminder delivery counters and quality summary.
- 2026-02-27: Added smoke `agent/reminder_retry_backoff_smoke.py` covering transient success, transient exhaustion, and non-transient failure branches.
- 2026-02-27: Smoke checks passed: `py_compile`, retry smoke, idempotency smoke, reminders-only mock dry-run.

## Links
- Jira: DTM-41
- Files: core/reminder.py, core/planner.py, agent/reminder_retry_backoff_smoke.py, doc/05_risk_register.md
