# DTM-51: TSK-054 Stage 5 follow-up: CI wrapper command for evaluator (`--fail-profile ci`)

## Context
- Reminder alert evaluator already supports profile-based severity gate (`local|ci`).
- Routine ops docs still reference direct Python call; CI usage is not standardized as a wrapper command.
- Sprint next queue includes dedicated CI wrapper for deterministic routine checks.

## Goal
- Add stable wrapper command for evaluator CI mode.
- Ensure docs reference wrapper for routine CI checks.
- Keep Jira/agile lifecycle synchronized for this single-task execution block.

## Non-goals
- No threshold formula changes.
- No evaluator logic changes.
- No owner-notify behavior changes.

## Plan
1. Add root-level CI wrapper command for evaluator (`--fail-profile ci`).
2. Update routine docs to reference wrapper command.
3. Sync sprint/context/backlog state and Jira evidence.
4. Run smoke checks for wrapper and evaluator flow.

## Checklist (DoD)
- [x] Wrapper command exists and propagates evaluator exit code.
- [x] Routine docs reference wrapper command for CI checks.
- [x] Smoke checks pass for wrapper/evaluator paths.
- [x] Jira status/comments and agile docs are synchronized.

## Work log
- 2026-02-27: Jira `DTM-51` created and moved to `Ð’ Ñ€Ð°Ð±Ð¾Ñ‚Ðµ`; start evidence comment added.
- 2026-02-27: Freshness/trust check completed for evaluator wrapper scope (`agent/reminder_alert_evaluator.py`, `run_timer.cmd`, `README.md`, `doc/ops/baseline_validation_and_artifacts.md`).
- 2026-02-27: Added `run_alert_eval_ci.cmd` wrapper and aligned routine docs to use wrapper command for CI gate.
- 2026-02-27: Smoke checks passed (`run_alert_eval_ci.cmd --help`, INFO sample exit=0, WARN sample exit=2, `.venv\Scripts\python.exe agent\reminder_alert_evaluator_smoke.py`).

## Links
- Jira: DTM-51
- Sources: agent/reminder_alert_evaluator.py, run_timer.cmd, README.md, doc/ops/baseline_validation_and_artifacts.md
