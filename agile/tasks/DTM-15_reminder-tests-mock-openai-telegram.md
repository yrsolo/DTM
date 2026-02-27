# DTM-15: Reminder tests - mock OpenAI and Telegram side effects

## Context
- Current reminder test/dry-check paths may call OpenAI API and send Telegram messages.
- For tests this is unnecessary, slow, and risks external side effects/costs.
- Owner requested adding this as non-urgent backlog work.

## Goal
- Ensure reminder tests can run without external OpenAI/Telegram calls.
- Define explicit mock/stub strategy for LLM generation and message delivery.

## Non-goals
- No change to production reminder behavior.
- No broad reminder pipeline refactor in this task.

## Mode
- Execution mode

## Plan
1) Locate integration boundaries in reminder path (`core/reminder.py`, run entrypoints).
2) Add test-mode switches or dependency injection points for OpenAI/Telegram clients.
3) Cover with focused tests that assert no external calls in test mode.
4) Document run/test commands and guardrails.

## Risks
- Accidental behavior drift between mocked and production paths.
- Partial mocking may leave hidden external calls.

## Acceptance Criteria
- Test run path executes reminder logic without real OpenAI requests.
- Test run path executes reminder logic without real Telegram sends.
- Existing production mode keeps current behavior.

## Checklist (DoD)
- [x] Mock/stub strategy implemented for OpenAI + Telegram in reminder tests.
- [x] Tests verify no external calls in test mode.
- [x] Smoke-check confirms production mode still unchanged.
- [x] Docs/sprint/Jira synced.

## Work log
- 2026-02-27: Jira issue created (DTM-15), kept in To Do as non-urgent owner request.
- 2026-02-27: Jira moved to `V rabote`; execution started.
- 2026-02-27: Added `MockOpenAIChatAgent` + reminder mock flags (`mock_openai`, `mock_telegram`) and threaded `mock_external` through planner/main/local_run (`--mock-external`).
- 2026-02-27: Smoke passed: `.venv\Scripts\python.exe local_run.py --mode test --dry-run --mock-external` and `.venv\Scripts\python.exe local_run.py --mode reminders-only --dry-run --mock-external`; Telegram sends skipped via `mock_telegram_send` logs.
- 2026-02-27: Docs synced (`README.md`, `doc/02_current_modules_and_functionality.md`, `doc/03_reconstruction_backlog.md`, sprint/context files) and Jira prepared for `Gotovo`.

## Links
- Jira: DTM-15
- Sprint: agile/sprint_current.md
