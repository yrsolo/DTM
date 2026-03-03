# Stage 17 Closeout And Stage 18 Handoff

## Stage 17 summary (done)
Delivered group-chat query capability for the bot. Designers can now tag/command bot in group and receive current personal tasks or nearest team deadlines directly in that same group chat.

## Why it matters
- Removes friction of checking deadlines manually.
- Makes bot useful in team chat context (not only scheduled morning pushes).

## Evidence
- Runtime path:
  - `index.py`
  - `core/group_query.py`
- Smoke:
  - `agent/group_query_smoke.py`
  - `agent/reminder_fallback_smoke.py`
- Docs:
  - `README.md`
  - `doc/stages/51..54`

## Stage 18 proposal
- Focus: provider reliability policy and failover constraints.
- Initial estimate: 5 tasks.
- Planned outcomes:
  1. reliability matrix by provider,
  2. timeout/retry guardrails by provider,
  3. fallback policy (draft vs alternate provider),
  4. provider-level counters and alert signals,
  5. closeout and ops handoff.
