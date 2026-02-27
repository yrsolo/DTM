# DTM-46: TSK-049 Stage 5 controlled owner-notify trigger from evaluator output

## Context
- Alert evaluator already computes `INFO_ONLY/WARN/CRITICAL` but does not trigger owner notifications.
- Escalation policy in risk register requires owner notify on `CRITICAL`.
- Trigger must be controlled and opt-in to avoid unintended external side effects.

## Goal
- Add controlled owner-notify trigger from evaluator output with explicit CLI opt-in.
- Keep default behavior unchanged (no notify by default).
- Wire this control through local run and baseline capture flows.

## Non-goals
- No automatic always-on notifications.
- No changes to thresholds logic itself.
- No changes to reminder send pipeline.

## Plan
1. Extend evaluator with notify control flags and helper call (`notify_owner.py`).
2. Add local run flags and invoke notify only when explicitly configured.
3. Pass notify controls through baseline capture utility.
4. Add/extend smoke checks and sync docs/Jira/sprint/context.

## Checklist (DoD)
- [x] Notify trigger is opt-in and disabled by default.
- [x] Severity gating (`warn|critical`) works as configured.
- [x] Smoke checks pass (`py_compile`, evaluator smoke, local reminders dry-run).
- [x] Jira and process docs synchronized.

## Work log
- 2026-02-27: Jira `DTM-46` created and moved to `V rabote`; start evidence comment added.
- 2026-02-27: Freshness/trust check completed for evaluator/local_run/capture_baseline/notify integration points.
- 2026-02-27: Added controlled notify flags in evaluator (`--notify-owner-on`, `--notify-owner-context`, `--notify-owner-dry-run`) and notify helper integration.
- 2026-02-27: Added local-run notify controls and auto-evaluation when notify gate is enabled.
- 2026-02-27: Added baseline-capture passthrough for notify controls.
- 2026-02-27: Extended evaluator smoke with notify dry-run coverage; validated py_compile, evaluator smoke, local reminders dry-run, and baseline capture retry smoke.

## Links
- Jira: DTM-46
- Files: agent/reminder_alert_evaluator.py, local_run.py, agent/capture_baseline.py, agent/reminder_alert_evaluator_smoke.py
