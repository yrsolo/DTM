# DTM-55: TSK-058 Stage 6 kickoff: dynamic estimate tracker and completion-notify process rule

## Context
- Stage 5 is completed and Stage 6 starts from planning and decomposition.
- Owner requested continuous visibility: always report current stage estimate as `done/remaining`.
- Owner requested Telegram update after each completed task.

## Goal
- Introduce explicit Stage 6 dynamic estimate tracking in sprint board.
- Formalize operational rule to send Telegram notification on each task completion.

## Non-goals
- No runtime code behavior changes.
- No Stage 6 implementation slices yet (read-model/UI work starts next tasks).

## Plan
1. Verify freshness/trust of Stage 6 planning sources (`doc/03`, `agile/sprint_current.md`, `AGENTS.md`).
2. Update sprint board with Stage 6 baseline estimate and done/remaining counters.
3. Record owner process directive in sprint notes and task artifacts.
4. Sync backlog/context docs and Jira lifecycle.

## Checklist (DoD)
- [x] Stage 6 estimate is visible in sprint as `baseline/done/remaining`.
- [x] Owner directive about completion Telegram notify is documented.
- [x] Context registry includes trust entry for Stage 6 kickoff sources.
- [x] Jira lifecycle and evidence comments are complete.

## Work log
- 2026-02-27: Jira `DTM-55` created and moved to `В работе`; start evidence comment posted.
- 2026-02-27: Stage 6 kickoff updates started in sprint board and process notes.
- 2026-02-27: Stage 6 tracker initialized in sprint board (baseline 8, done 1, remaining 7) and owner directive added: Telegram notification after each task completion.
- 2026-02-27: Smoke checks passed (`.venv\Scripts\python.exe agent\notify_owner.py --help`, `.venv\Scripts\python.exe agent\capture_baseline.py --help`).

## Links
- Jira: DTM-55
- Sources: agile/sprint_current.md, agile/context_registry.md, doc/03_reconstruction_backlog.md, AGENTS.md
