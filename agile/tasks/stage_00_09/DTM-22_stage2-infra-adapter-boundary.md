# DTM-22: Stage 2 infrastructure adapter boundary for external services

## Context
- Stage 2 already extracted bootstrap and application use-cases.
- Reminder flow still couples domain orchestration with concrete external service classes.

## Goal
- Introduce explicit adapter boundary contracts for external integrations (OpenAI/Telegram).
- Shift reminder/bootstrap wiring to use injected adapter interfaces.

## Non-goals
- No major rewrite of repository/sheets adapters in this task.
- No behavioral changes in reminder delivery logic.

## Mode
- Execution mode

## Plan
1) Add adapter protocol contracts module for external services.
2) Update reminder abstractions to consume injected adapter interfaces.
3) Update bootstrap wiring to construct and inject concrete adapters explicitly.
4) Run smoke checks and sync docs/sprint/Jira.

## Risks
- Interface mismatch can break runtime during async calls.
- Hidden fallback path might still instantiate concrete adapters in domain flow.

## Acceptance Criteria
- Adapter protocols exist and are used in reminder/bootstrap path.
- Reminder can operate with injected Telegram/OpenAI adapters.
- Existing run modes pass smoke checks.

## Checklist (DoD)
- [x] Freshness/trust evidence recorded.
- [x] Adapter boundary contracts and injection wiring implemented.
- [x] Smoke checks passed.
- [x] Sprint/docs/Jira synced.

## Work log
- 2026-02-27: Jira `DTM-22` moved to `V rabote`; execution started.
- 2026-02-27: Added `core/adapters.py` with external adapter protocols (`ChatAdapter`, `MessageAdapter`, `LoggerAdapter`) and `NullLogger`.
- 2026-02-27: Updated `core/reminder.py` to consume injected adapters (`openai_agent`, `telegram_adapter`) and removed default side-effect logger instantiation.
- 2026-02-27: Updated `core/bootstrap.py` to explicitly construct and inject concrete Telegram/OpenAI adapters through dependency wiring.
- 2026-02-27: Smoke passed: `py_compile core/adapters.py core/reminder.py core/bootstrap.py`, `local_run.py --mode sync-only --dry-run`, `local_run.py --mode reminders-only --dry-run --mock-external`.

## Links
- Jira: DTM-22
- Sprint: agile/sprint_current.md
