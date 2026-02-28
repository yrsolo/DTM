# DTM-164: Stage 14 notification semantics split (`blocked` vs `info`)

## Context
- Owner notifications were interpreted as action-required even when work continued autonomously.

## Goal
- Make notification intent explicit via runtime mode flag and usage convention.

## Non-goals
- Changing Telegram transport or token storage.

## Plan
1. Extend notifier CLI with explicit mode.
2. Set informative flows to `info`.
3. Update process command examples for blocker flows.
4. Run smoke checks.

## Checklist (DoD)
- [x] `agent/notify_owner.py` supports `--mode blocked|info`.
- [x] Alert evaluator uses `--mode info`.
- [x] Blocker commands in docs use `--mode blocked`.
- [x] Smoke checks passed.

## Work log
- 2026-02-28: Implemented mode split and updated owner-escalation command templates.
- 2026-02-28: Smoke passed (`agent/notify_owner_payload_smoke.py`, `agent/reminder_alert_evaluator_smoke.py`).

## Links
- `agent/notify_owner.py`
- `agent/reminder_alert_evaluator.py`
- `AGENTS.md`
- `agent/OPERATING_CONTRACT.md`
- `agent/teamlead.md`
- `agent/teamlead_chat_prompt.md`
- `doc/stages/41_stage14_owner_notification_and_transition_standard.md`