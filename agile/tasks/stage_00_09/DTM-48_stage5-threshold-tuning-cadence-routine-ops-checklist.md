# DTM-48: TSK-051 Stage 5 follow-up: encode threshold tuning cadence into routine ops checklist

## Context
- Stage 5 already has threshold policy and tuning loop, but recurring operational cadence is still implicit.
- Team needs deterministic checklist timing (per run / weekly / monthly) for threshold tuning governance.
- Current baseline and evaluator docs require an explicit routine-ops checklist section.

## Goal
- Formalize threshold tuning cadence in runbook/checklist docs.
- Keep the process executable with clear owner actions and evidence artifacts.
- Sync sprint/context/Jira lifecycle for this docs/process increment.

## Non-goals
- No changes to threshold formulas.
- No changes to evaluator runtime logic.
- No changes to Telegram notify trigger behavior.

## Plan
1. Verify freshness of Stage 5 ops sources (`doc/02`, `doc/05`, `README`, evaluator/baseline scripts).
2. Add explicit routine cadence checklist (per-run/weekly/monthly) and evidence expectations.
3. Sync `agile/context_registry.md`, `agile/sprint_current.md`, and `doc/03_reconstruction_backlog.md`.
4. Run lightweight smoke checks for referenced commands and close Jira lifecycle.

## Checklist (DoD)
- [x] Routine cadence checklist documented with concrete periodicity and owner action points.
- [x] No drift between risk-register policy and baseline runbook/checklist.
- [x] Relevant smoke checks pass for referenced CLI flow.
- [x] Jira comments/status and sprint/task/context docs are synchronized.

## Work log
- 2026-02-27: Jira `DTM-48` created and moved to `V rabote`; start evidence comment posted.
- 2026-02-27: Freshness/trust check completed via `git log`/`git blame` for `doc/02`, `doc/05`, `README`, `agent/capture_baseline.py`, `agent/reminder_alert_evaluator.py`.
- 2026-02-27: Added explicit routine cadence checklist (per-run / weekly / monthly) and aligned risk-register policy references.
- 2026-02-27: Smoke checks passed for referenced CLI flow (`agent/capture_baseline.py --help`, `agent/reminder_alert_evaluator.py --help`, `local_run.py --help`).

## Links
- Jira: DTM-48
- Sources: doc/ops/baseline_validation_and_artifacts.md, doc/05_risk_register.md, README.md, agent/capture_baseline.py
