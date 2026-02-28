# Stage 20 Doc/Agile Freshness Audit

## Scope
- `README.md`
- `doc/00_documentation_map.md`
- `doc/03_reconstruction_backlog.md`
- `agile/sprint_current.md`
- `agile/context_registry.md`

## Verification method
1. Compared active docs to current runtime contour in code:
   - multi-LLM provider support and failover (`config/constants.py`, `core/reminder.py`, `core/bootstrap.py`),
   - group-chat query flow (`index.py`, `core/group_query.py`),
   - deploy and smoke helper scripts (`agent/*smoke.py`, deploy workflow).
2. Checked active sprint state vs backlog state.
3. Removed stale, duplicated historical detail from active backlog doc.

## Findings
- `doc/03_reconstruction_backlog.md` contained stale and over-detailed historical lists, including outdated phrasing about pending kickoff.
- `README.md` project-status section duplicated many stage-by-stage links and reduced readability.
- `doc/00_documentation_map.md` stage package section was incomplete for later stages.

## Actions taken
- Rewrote `doc/03_reconstruction_backlog.md` to compact current-state format with Stage 20 in progress.
- Reduced `README.md` project-status section to active pointers and runbooks.
- Refreshed `doc/00_documentation_map.md` stage package index through Stage 19 + Stage 20 pointer.
- Updated `.gitignore` to include `web_prototype/__pycache__/` to avoid local noise in git status.

## Result
- Active docs now prioritize current execution state and primary entrypoints.
- Historical detail stays in archive/stage documents, not in active backlog overview.
- Stage 20 can continue with structure hygiene and release-readiness evidence without context drift.
