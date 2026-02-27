# DTM-43: TSK-046 Stage 5 wire threshold evaluator output into alert-review workflow

## Context
- Threshold evaluator exists (`agent/reminder_alert_evaluator.py`) and can classify `INFO_ONLY/WARN/CRITICAL`.
- Baseline and local review flows generate `quality_report` artifacts but do not always persist evaluator output as first-class review artifact.
- Stage 5 requires operational review flow to include evaluator result without auto-side-effects.

## Goal
- Wire evaluator output artifact into local/baseline review workflow.
- Keep behavior side-effect free (no automatic Jira/Telegram actions).

## Non-goals
- No automatic owner notifications from this slice.
- No threshold value changes.

## Plan
1. Integrate evaluator output generation into local run review flow.
2. Integrate evaluator artifact generation into baseline capture bundle.
3. Add deterministic smoke for alert-review wiring.
4. Sync docs/sprint/context/backlog and Jira evidence.

## Checklist (DoD)
- [x] Evaluator output wired into local review flow.
- [x] Baseline bundle includes `alert_evaluation.json`.
- [x] Deterministic smoke passes.
- [x] Jira/docs/sprint/context synchronized.

## Work log
- 2026-02-27: Jira `DTM-43` created, moved to `В работе`, start evidence comment added.
- 2026-02-27: `local_run.py` extended with alert-evaluation wiring (`--evaluate-alerts`, `--alert-evaluation-file`, `--alert-fail-on`) using in-process evaluator helpers.
- 2026-02-27: `agent/capture_baseline.py` extended to include `alert_evaluation.json` in baseline bundle.
- 2026-02-27: Added deterministic smoke `agent/reminder_alert_review_flow_smoke.py`.
- 2026-02-27: Smoke checks passed (`py_compile`, review-flow smoke, local run with alert evaluation, baseline capture smoke).

## Links
- Jira: DTM-43
- Files: local_run.py, agent/capture_baseline.py, agent/reminder_alert_review_flow_smoke.py
