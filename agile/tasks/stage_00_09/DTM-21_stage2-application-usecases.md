# DTM-21: Stage 2 application use-case orchestration extraction

## Context
- `main.py` still contains orchestration logic for mode resolution and pipeline execution branches.
- Stage 2 target requires explicit application-layer use-cases separate from interfaces entrypoint.

## Goal
- Extract orchestration flow from `main.py` into dedicated application use-case module.
- Keep runtime behavior unchanged for all existing run modes.

## Non-goals
- No infrastructure adapter redesign in this task (DTM-22 scope).
- No changes in planner business logic semantics.

## Mode
- Execution mode

## Plan
1) Introduce application use-case module for mode resolution + planner flow execution.
2) Rewire `main.py` to delegate orchestration to that module.
3) Keep existing output/quality report behavior intact.
4) Run smoke checks and sync docs/sprint/Jira.

## Risks
- Behavior drift in mode resolution from event payloads.
- Missed branch in sync/reminder execution path.

## Acceptance Criteria
- `main.py` becomes thin interface wrapper delegating orchestration.
- New use-case module owns mode resolution and run-branch execution.
- Existing run modes work in smoke checks.

## Checklist (DoD)
- [x] Freshness/trust evidence recorded.
- [x] Use-case module extracted and wired.
- [x] Smoke checks passed.
- [x] Sprint/docs/Jira synced.

## Work log
- 2026-02-27: Jira `DTM-21` moved to `V rabote`; execution started.
- 2026-02-27: Added `core/use_cases.py` (`resolve_run_mode`, `run_planner_use_case`) and rewired `main.py` to delegate orchestration to application use-cases.
- 2026-02-27: Smoke passed: `py_compile core/use_cases.py main.py`, `local_run.py --mode sync-only --dry-run`, `local_run.py --mode reminders-only --dry-run --mock-external`.

## Links
- Jira: DTM-21
- Sprint: agile/sprint_current.md
