# DTM-173: Stage 16 runtime adapter expansion (OpenAI/Google/Yandex)

## Context
- Reminder enhancement path was hardcoded to OpenAI adapter.
- Required outcome: runtime-selectable LLM provider without changing reminder orchestration contract.

## Goal
- Add Google and Yandex async chat adapters and provider selection in bootstrap.

## Non-goals
- Cross-provider fallback chain in one run.
- Provider-specific prompt tuning.

## Plan
1. Add provider env contour in `config/constants.py`.
2. Implement Google and Yandex adapters in `core/reminder.py`.
3. Switch bootstrap chat adapter factory to `LLM_PROVIDER`.

## Checklist (DoD)
- [x] `LLM_PROVIDER` supports `openai|google|yandex`.
- [x] Bootstrap factory returns provider-specific adapter.
- [x] Existing OpenAI and mock flow remain backward-compatible.

## Work log
- 2026-02-28: Added provider constants, new adapters, and bootstrap provider switch.

## Links
- `config/constants.py`
- `core/reminder.py`
- `core/bootstrap.py`
