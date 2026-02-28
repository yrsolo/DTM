# DTM-183: Stage 18 reliability runtime guardrails

## Context
- Multi-provider LLM runtime exists (`openai/google/yandex`), but timeout/retry policy was implicit.

## Goal
- Add configurable timeout/retry/backoff guardrails for provider calls.
- Expose enhancer counters in runtime quality report.

## Non-goals
- Alternate provider fallback chain.

## Plan
1. Add LLM HTTP reliability env settings in config.
2. Apply retry guard in OpenAI/Google/Yandex adapters.
3. Add enhancer counters in `Reminder` and surface them in planner report.

## Checklist (DoD)
- [x] `LLM_HTTP_TIMEOUT_SECONDS`, `LLM_HTTP_RETRY_ATTEMPTS`, `LLM_HTTP_RETRY_BACKOFF_SECONDS` added.
- [x] Adapter retry/timeout logic implemented.
- [x] Enhancer counters added to summary/report.

## Work log
- 2026-02-28: Reliability settings and counters implemented.

## Links
- `config/constants.py`
- `core/reminder.py`
- `core/bootstrap.py`
- `core/planner.py`
