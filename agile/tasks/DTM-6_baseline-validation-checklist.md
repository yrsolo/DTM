# DTM-6: Baseline validation checklist and artifact capture flow

## Context
- Stage 0.4 requires repeatable baseline validation after each pipeline change.
- Current flow has smoke commands, but no single checklist + artifact capture entrypoint.

## Goal
- Add a reproducible baseline validation flow:
  - one command to capture dry-run artifact bundle,
  - checklist for manual comparison against baseline.

## Acceptance Criteria
- `agent/capture_baseline.py` produces timestamped artifact bundle with log, meta, and checklist files.
- `README.md` links to baseline capture command.
- Stage 0.4 backlog section has explicit status update.
- Smoke-check command for capture flow passes in project virtualenv.

## Risks
- Dry-run logs can still be noisy for large sheets; keep evidence concise in Jira comments.
- Artifact folder can grow quickly; generated outputs must remain untracked by git.

## Non-goals
- No business logic changes in planner/reminder behavior.
- No production deployment changes.

## Mode
- Execution mode

## Plan
1) Add artifact capture helper for `sync-only --dry-run`.
2) Add baseline checklist document and artifact folder structure.
3) Update README/sprint docs and validate with smoke-check.

## Checklist (DoD)
- [x] Baseline capture helper creates timestamped artifact folder with logs/meta.
- [x] Checklist documents mandatory comparison points (shape, key cells, notes/colors).
- [x] README references the baseline flow command.
- [x] Jira lifecycle/status/comments updated with evidence.

## Work log
- 2026-02-27: Task created in Jira as DTM-6 and moved to `В работе`.
- 2026-02-27: TeamLead started implementation from clean sprint state after DTM-5 completion.
- 2026-02-27: Added `agent/capture_baseline.py` and baseline process doc `doc/02_baseline_validation_and_artifacts.md`.
- 2026-02-27: Smoke-check passed:
  - `.venv\Scripts\python.exe agent\capture_baseline.py --help`
  - `.venv\Scripts\python.exe agent\capture_baseline.py --label tsk007_smoke`
- 2026-02-27: Jira comment with evidence added; issue transitioned to `Готово`.

## Links
- Jira: DTM-6
- Notes: doc/03_reconstruction_backlog.md (section 0.4)
