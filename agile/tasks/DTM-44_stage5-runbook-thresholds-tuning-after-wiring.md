# DTM-44: TSK-047 Stage 5 runbook and thresholds tuning after evaluator wiring rollout

## Context
- Alert evaluator and review-flow wiring are implemented (`DTM-42`, `DTM-43`).
- Operational runbook and baseline validation doc must reflect new artifact `alert_evaluation.json`.
- Threshold tuning process should be explicit and reproducible for TeamLead iterations.

## Goal
- Update runbook docs to include evaluator-wired review workflow.
- Define explicit threshold tuning loop and evidence requirements.

## Non-goals
- No runtime threshold code changes.
- No automatic external notifications from this doc slice.

## Plan
1. Update baseline/runbook documentation with alert-evaluation artifact checks.
2. Document threshold tuning loop and review cadence.
3. Sync sprint/context/backlog and Jira evidence.
4. Run smoke for evaluator flow to validate documented commands.

## Checklist (DoD)
- [x] Runbook docs updated for evaluator-wired workflow.
- [x] Threshold tuning policy explicitly documented.
- [x] Smoke command(s) from runbook executed successfully.
- [x] Jira/docs/sprint/context synchronized.

## Work log
- 2026-02-27: Jira `DTM-44` created, moved to `Ð’ Ñ€Ð°Ð±Ð¾Ñ‚Ðµ`, start evidence comment added.
- 2026-02-27: Updated `doc/ops/baseline_validation_and_artifacts.md` with evaluator-wired baseline command and `alert_evaluation.json` artifact expectations.
- 2026-02-27: Added explicit threshold tuning loop in `doc/05_risk_register.md`.
- 2026-02-27: Runbook smoke executed with baseline capture command and successful artifact generation.

## Links
- Jira: DTM-44
- Docs: doc/ops/baseline_validation_and_artifacts.md, doc/05_risk_register.md
