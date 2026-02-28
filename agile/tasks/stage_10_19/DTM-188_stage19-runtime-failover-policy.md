# DTM-188: Stage 19 runtime failover policy

## Context
- Multi-provider runtime exists, but fallback behavior needed explicit policy.

## Goal
- Implement policy modes:
  - `draft_only`: fallback only to draft message.
  - `provider`: if primary enhancer returns empty/error, try fallback provider.

## Non-goals
- Multi-hop fallback chain.

## Plan
1. Add failover env settings.
2. Add fallback adapter wrapper.
3. Wire policy in bootstrap and surface counters.

## Checklist (DoD)
- [x] `LLM_FAILOVER_MODE` and `LLM_FAILOVER_PROVIDER` added.
- [x] `FallbackChatAdapter` implemented and wired.
- [x] Quality report includes failover counters.

## Work log
- 2026-02-28: Runtime failover policy delivered.

## Links
- `config/constants.py`
- `core/reminder.py`
- `core/bootstrap.py`
- `core/planner.py`
