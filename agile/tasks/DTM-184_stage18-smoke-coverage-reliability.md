# DTM-184: Stage 18 smoke coverage for reliability contour

## Context
- New reliability/counter logic requires deterministic local checks.

## Goal
- Add and run smoke checks for enhancer counters and provider bootstrap.

## Non-goals
- Live provider integration tests.

## Plan
1. Add `agent/reminder_enhancer_counters_smoke.py`.
2. Extend fallback smoke assertions.
3. Execute compile/smoke package.

## Checklist (DoD)
- [x] New smoke script added and passing.
- [x] Existing fallback and provider-smoke still green.
- [x] Evidence reflected in stage docs/context registry.

## Work log
- 2026-02-28: Added and executed reliability smoke suite.

## Links
- `agent/reminder_enhancer_counters_smoke.py`
- `agent/reminder_fallback_smoke.py`
- `agent/llm_provider_bootstrap_smoke.py`
