# DTM-52: TSK-055 Stage 5 follow-up: monthly alert-threshold drift review note in sprint ceremony template

## Context
- Stage 5 cadence already defines monthly threshold drift review in ops docs.
- Sprint ceremony template did not explicitly require this monthly review checkpoint.
- Sprint next queue includes this follow-up governance item.

## Goal
- Add explicit monthly alert-threshold drift review note into sprint ceremony template.
- Keep sprint/context/backlog/Jira synchronized for this process increment.

## Non-goals
- No runtime behavior changes.
- No threshold value changes.
- No notifier policy changes.

## Plan
1. Verify freshness of ceremony and Stage 5 ops policy sources.
2. Update ceremony template with explicit monthly drift review step.
3. Sync sprint/context/backlog and Jira lifecycle.
4. Run lightweight docs smoke checks for referenced commands.

## Checklist (DoD)
- [x] Ceremony template includes explicit monthly drift review note.
- [x] Sprint/context/backlog docs synchronized with DTM-52 status.
- [x] Jira status/comment lifecycle completed with evidence.
- [x] Smoke checks for referenced command surfaces passed.

## Work log
- 2026-02-27: Jira `DTM-52` created and moved to `В работе`; start evidence comment posted.
- 2026-02-27: Freshness/trust check completed for `agile/retro.md`, `agile/sprint_current.md`, `doc/02_baseline_validation_and_artifacts.md`, and `doc/05_risk_register.md`.
- 2026-02-27: Added monthly alert-threshold drift review checkpoint into `agile/retro.md` ceremony checklist template.
- 2026-02-27: Smoke checks passed (`.venv\\Scripts\\python.exe agent\\capture_baseline.py --help`, `.venv\\Scripts\\python.exe agent\\reminder_alert_evaluator.py --help`).

## Links
- Jira: DTM-52
- Sources: agile/retro.md, agile/sprint_current.md, doc/02_baseline_validation_and_artifacts.md, doc/05_risk_register.md
