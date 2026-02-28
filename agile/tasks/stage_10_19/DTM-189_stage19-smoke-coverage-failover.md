# DTM-189: Stage 19 smoke coverage for failover

## Context
- Failover policy needs deterministic validation.

## Goal
- Add smokes for failover mode and bootstrap mapping.

## Non-goals
- Live external provider failover runs.

## Plan
1. Add `agent/llm_failover_provider_smoke.py`.
2. Extend bootstrap smoke with failover selection check.
3. Re-run enhancer counters smoke.

## Checklist (DoD)
- [x] New failover smoke added and passing.
- [x] Bootstrap smoke validates fallback provider wiring.
- [x] Enhancer counters smoke remains green.

## Work log
- 2026-02-28: Failover smoke package executed.

## Links
- `agent/llm_failover_provider_smoke.py`
- `agent/llm_provider_bootstrap_smoke.py`
