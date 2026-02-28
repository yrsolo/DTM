# DTM-50: TSK-053 Stage 5 follow-up: controlled owner notify message template hardening (RU-only payload validation)

## Context
- Owner notification flow exists and is wired from evaluator/local run.
- `agent/notify_owner.py` currently sends message wrapper/labels in English and does not enforce Russian-only payload requirements.
- Process contract requires Telegram notifications in Russian with clear next action.

## Goal
- Harden owner-notify templates to Russian wording.
- Add explicit RU-only payload validation guard before sending Telegram message.
- Align evaluator/local defaults so generated notify payload is compliant.

## Non-goals
- No threshold/risk formula changes.
- No retry/backoff logic changes.
- No Jira process rule changes.

## Plan
1. Add RU-only payload validation and Russian message envelope in `agent/notify_owner.py`.
2. Normalize evaluator notify payload fields to Russian-only wording.
3. Align default notify context strings in launcher/baseline helper to Russian wording.
4. Sync docs/sprint/context/Jira and run relevant smoke checks.

## Checklist (DoD)
- [x] RU-only validation enforced for owner notify payload.
- [x] Evaluator notify payload is Russian-only and process-compliant.
- [x] Smoke checks pass (`notify_owner --help`, evaluator smoke, local reminders dry-run notify-dry-run).
- [x] Jira and agile/docs state fully synchronized.

## Work log
- 2026-02-27: Jira `DTM-50` created and moved to `V rabote`; start evidence comment posted.
- 2026-02-27: Freshness/trust check completed for notify sources (`agent/notify_owner.py`, `agent/reminder_alert_evaluator.py`, `local_run.py`, `agent/capture_baseline.py`) via git history/blame/symbol scan.
- 2026-02-27: Added RU-only payload validation guard and Russian envelope in `agent/notify_owner.py` with unicode-safe console output.
- 2026-02-27: Normalized evaluator notify payload templates to Russian-only wording and adjusted default notify context in launcher/baseline flow.
- 2026-02-27: Smoke passed (`py_compile`, `notify_owner_payload_smoke.py`, `reminder_alert_evaluator_smoke.py`, `local_run.py --mode reminders-only --dry-run --mock-external --evaluate-alerts --alert-fail-on none --notify-owner-on warn --notify-owner-dry-run`).

## Links
- Jira: DTM-50
- Sources: agent/notify_owner.py, agent/reminder_alert_evaluator.py, local_run.py, agent/capture_baseline.py, doc/05_risk_register.md
