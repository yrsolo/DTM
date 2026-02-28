# DTM-174: Stage 16 provider bootstrap smoke

## Context
- Provider selection was added in runtime bootstrap and needs deterministic local verification.

## Goal
- Add smoke script validating provider-to-adapter mapping without external API calls.

## Non-goals
- Live external provider integration tests.

## Plan
1. Add smoke helper script for bootstrap adapter selection.
2. Validate `openai/google/yandex` mappings and `mock_external` path.
3. Include smoke command in Stage 16 evidence.

## Checklist (DoD)
- [x] Script exists in `agent/`.
- [x] Script validates provider classes and mock class.
- [x] Smoke run passes locally.

## Work log
- 2026-02-28: Added `agent/llm_provider_bootstrap_smoke.py` and executed pass run.

## Links
- `agent/llm_provider_bootstrap_smoke.py`
