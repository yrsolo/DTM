# DTM-39: TSK-042 Stage 5 alerting thresholds and escalation policy for reminder delivery metrics

## Context
- Stage 4/5 already introduced reminder delivery counters and derived SLI fields.
- Risk register (`R-008`) still marked alerting/escalation policy as pending.
- Owner escalation flow exists (`agent/notify_owner.py`) but reminder metric thresholds were not formalized.

## Goal
- Define explicit alert thresholds for reminder delivery SLI based on existing runtime fields.
- Define a concrete escalation sequence and owner next action for warning/critical states.

## Non-goals
- No runtime code changes in reminder pipeline.
- No external alerting platform integration in this slice.

## Plan
1. Verify available reminder SLI/counter fields in code and docs.
2. Add threshold + escalation policy to risk register.
3. Sync sprint/task/context docs and Jira evidence.
4. Run reminders-only dry-run mock sanity check.

## Checklist (DoD)
- [x] Alert thresholds documented with exact metric names.
- [x] Escalation policy documented with owner next actions.
- [x] Sprint/context/task docs synchronized.
- [x] Smoke sanity-check executed.

## Work log
- 2026-02-27: Jira `DTM-39` created, moved to `В работе`, start evidence added.
- 2026-02-27: Freshness check completed against `core/planner.py` SLI fields and `core/reminder.py` counters.
- 2026-02-27: Threshold and escalation policy added to `doc/05_risk_register.md`.
- 2026-02-27: Sprint and context registry synchronized for this Stage 5 slice.
- 2026-02-27: Sanity smoke run completed: `local_run.py --mode reminders-only --dry-run --mock-external`.

## Links
- Jira: DTM-39
- Docs: doc/05_risk_register.md, agile/sprint_current.md, agile/context_registry.md
