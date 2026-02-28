# DTM-47: TSK-050 Stage 5 evaluator severity gate policy for CI/local exit behavior

## Context
- Evaluator already supports severity exit gate via `--fail-on`, but CI/local policy is not formalized as an explicit runtime profile.
- Local runs default to non-blocking (`--alert-fail-on none`), while CI expectations should be stricter and reproducible.
- Team needs a deterministic policy mapping that is easy to invoke and override.

## Goal
- Add explicit CI/local gate policy profiles for evaluator exit behavior.
- Keep local default safe and non-blocking.
- Preserve explicit override semantics for `--fail-on` / `--alert-fail-on`.

## Non-goals
- No threshold formula changes.
- No notifier policy changes.
- No reminder runtime behavior changes outside alert gate decision.

## Plan
1. Add shared fail-profile resolver in evaluator (`local|ci`) with explicit override precedence.
2. Add local launcher profile flag and route exit gate through resolver.
3. Extend evaluator smoke with profile mapping checks.
4. Sync sprint/context/docs and Jira evidence.

## Checklist (DoD)
- [x] Explicit profile policy implemented for evaluator/local launcher.
- [x] Override precedence documented and covered by smoke.
- [x] Smoke checks pass (`py_compile`, evaluator smoke, local reminders dry-run).
- [x] Jira and docs synchronized.

## Work log
- 2026-02-27: Jira `DTM-47` created and moved to `V rabote`; start evidence comment added.
- 2026-02-27: Freshness/trust check completed for evaluator/local-run severity gate code paths and docs.
- 2026-02-27: Implemented profile resolver (`local|ci`) + explicit override precedence in evaluator/local launcher and baseline helper flags.
- 2026-02-27: Smoke verified (`py_compile`, `agent/reminder_alert_evaluator_smoke.py`, `local_run.py --mode reminders-only --dry-run --mock-external --alert-fail-profile ci --notify-owner-on none`) and CI-profile exit gate sanity-checked on synthetic WARN report.

## Links
- Jira: DTM-47
- Files: agent/reminder_alert_evaluator.py, local_run.py, agent/reminder_alert_evaluator_smoke.py
