# DTM-49: TSK-052 Stage 5 follow-up: formalize retry taxonomy metrics into runbook checklist

## Context
- Retry/backoff and taxonomy counters are implemented (`DTM-41`, `DTM-45`) but routine review checklist for these metrics is not explicit.
- Stage 5 ops needs deterministic checks for retry attempts/exhaustion and transient/permanent/unknown error mix.
- Baseline helper checklist should include these checks to keep incident triage consistent.

## Goal
- Add explicit retry taxonomy metrics checklist to runbook docs and baseline checklist template.
- Ensure metric names and expected interpretations are documented for TeamLead evidence comments.
- Sync sprint/context/Jira lifecycle for this docs/process increment.

## Non-goals
- No retry algorithm/code changes.
- No threshold formula changes for alert evaluator.
- No notifier behavior changes.

## Plan
1. Verify freshness of retry taxonomy sources (`core/reminder.py`, `core/planner.py`, retry smoke, docs).
2. Add checklist sections for retry/taxonomy metrics in `doc/02` and `doc/05`.
3. Update baseline helper checklist template to include retry taxonomy verification items.
4. Sync agile docs and Jira, then run smoke checks for referenced flow.

## Checklist (DoD)
- [x] Runbook checklist includes retry taxonomy metrics and review cadence.
- [x] Baseline helper checklist template includes retry taxonomy checks.
- [x] Metric names in docs match runtime quality summary fields.
- [x] Smoke checks pass and Jira/sprint/context/task docs are synchronized.

## Work log
- 2026-02-27: Jira `DTM-49` created and moved to `V rabote`; start evidence comment posted.
- 2026-02-27: Freshness/trust check completed for retry taxonomy sources via `git log`/`git blame`/`rg`.
- 2026-02-27: Added retry taxonomy metrics checklist details into `doc/02` and `doc/05`, plus baseline helper template checklist extension.
- 2026-02-27: Smoke checks passed (`py_compile agent/capture_baseline.py`, `agent/capture_baseline.py --help`, `agent/reminder_retry_backoff_smoke.py`).

## Links
- Jira: DTM-49
- Sources: core/reminder.py, core/planner.py, agent/reminder_retry_backoff_smoke.py, doc/02_baseline_validation_and_artifacts.md, doc/05_risk_register.md
