# Sprint Retro

## What Went Well
- Clear branch and merge discipline.
- Faster iterations due to explicit status reporting.
- Stage boundary communication became decision-ready (`past/next/estimate/go-no-go`).

## What Was Hard
- Legacy behavior comparison takes manual effort.
- Process rules were spread across multiple files.

## Improvements
- Keep one active sprint board in `agile/sprint_current.md`.
- Trigger owner notifications immediately on blockers requiring decision.
- Keep Telegram notifications intent-explicit: `blocked` only when execution is paused, `info` when execution continues.

## Stage 11 Detailed Retrospective Scope
1. Build full timeline from Stage 0 to Stage 10 (decisions, incidents, fixes).
2. Group root causes into categories:
   - process gaps,
   - configuration drift,
   - runtime/environment mismatch,
   - insufficient tests/smoke coverage.
3. For each repeated issue, record:
   - first seen date,
   - recurrence count,
   - impact/cost,
   - existing mitigation quality.
4. Convert findings into corrective tasks with:
   - owner,
   - deadline,
   - measurable verification signal.
5. Approve final retrospective package before Stage 12 start.

## Ceremony Checklist Template
- Review completed sprint goals and blockers.
- Confirm follow-up Jira items for unresolved risks.
- Monthly (first retro of month): run alert-threshold drift review using recent baseline bundles and `alert_evaluation.json`, then record decision (`no tuning` / `tuning proposed`) in sprint notes.
