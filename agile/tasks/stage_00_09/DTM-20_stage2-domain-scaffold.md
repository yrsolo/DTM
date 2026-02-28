# DTM-20: Stage 2 domain module extraction scaffold

## Context
- Stage 2 kickoff inventory (`doc/stages/10_stage2_layer_inventory.md`) identified first low-risk slice `S2-SLICE-01`.
- Current `GoogleSheetPlanner` constructor directly builds infrastructure dependencies, coupling orchestration and wiring.

## Goal
- Introduce Stage 2 scaffold that separates dependency construction boundary from planner orchestration.
- Keep runtime behavior unchanged across local/cloud entrypoints.

## Non-goals
- No broad module relocation of domain logic in this task.
- No behavior changes in timer/reminder business flow.

## Mode
- Execution mode

## Plan
1) Add bootstrap dependency builder module for planner wiring.
2) Update planner to consume prebuilt dependencies (with backward-compatible fallback).
3) Rewire `main.py` to use explicit bootstrap boundary.
4) Run smoke checks and sync docs/sprint/Jira.

## Risks
- Runtime regression if dependency wiring order/args drift.
- Hidden coupling paths still bypassing scaffold boundary.

## Acceptance Criteria
- New bootstrap module owns planner dependency construction.
- `GoogleSheetPlanner` can run with injected dependencies.
- `main.py` uses bootstrap builder, not direct constructor wiring only.
- Relevant smoke checks pass.

## Checklist (DoD)
- [x] Freshness/trust evidence recorded for Stage 2 sources.
- [x] Bootstrap scaffold implemented.
- [x] Local smoke checks passed.
- [x] Sprint/docs/Jira synced.

## Work log
- 2026-02-27: Jira `DTM-20` moved to `V rabote`; execution started.
- 2026-02-27: Added `core/bootstrap.py` with `build_planner_dependencies` + `PlannerDependencies` for planner wiring boundary.
- 2026-02-27: Updated `core/planner.py` to consume injected dependencies (with fallback bootstrap build) and rewired `main.py` to pass explicit dependencies.
- 2026-02-27: Smoke passed: `py_compile core/bootstrap.py core/planner.py main.py`, `local_run.py --mode sync-only --dry-run`, `local_run.py --mode reminders-only --dry-run --mock-external`.

## Links
- Jira: DTM-20
- Sprint: agile/sprint_current.md
- Stage 2 inventory: doc/stages/10_stage2_layer_inventory.md
