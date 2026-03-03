# DTM-19: Stage 2 layer boundary inventory and dependency map

## Context
- Stage 1 stabilization is complete; current `core/*` modules still mix domain rules, orchestration, and infrastructure calls.
- `doc/03_reconstruction_backlog.md` Stage 2 requires explicit layering (`domain`, `application`, `infrastructure`, `interfaces`).
- Safe decomposition requires an evidence-based dependency map before moving code.

## Goal
- Produce an explicit current-state layer inventory and dependency map.
- Define a low-risk first extraction slice for Stage 2 execution.

## Non-goals
- No broad code moves across modules in this task.
- No behavior changes in timer/reminder production flow.

## Mode
- Execution mode

## Plan
1) Verify freshness/trust of Stage 2 sources against current code and git history.
2) Build current module-to-layer inventory with concrete dependencies.
3) Define first extraction slice with acceptance criteria and risk constraints.
4) Sync sprint/docs/Jira and close issue lifecycle.

## Risks
- Incorrect boundary assumptions due to legacy mixed responsibilities.
- Over-scoped extraction plan creating regression risk for active runtime paths.

## Acceptance Criteria
- Stage 2 inventory document exists with current module ownership by layer.
- Dependency map identifies direct cross-layer coupling points.
- First extraction slice is concrete, reversible, and references target files.
- Sprint board and Jira statuses are synchronized.

## Checklist (DoD)
- [x] Freshness check recorded in `agile/context_registry.md`.
- [x] Stage 2 inventory/dependency map documented.
- [x] First extraction slice defined with risks and validation gate.
- [x] Sprint/Jira/docs synchronized.

## Work log
- 2026-02-27: Jira issue `DTM-19` created and moved to `V rabote`; execution started.
- 2026-02-27: Added `doc/stages/10_stage2_layer_inventory.md` with current module-to-layer mapping, cross-layer coupling points, and first low-risk extraction slice (`S2-SLICE-01`).
- 2026-02-27: Updated context registry trust evidence for Stage 2 sources and synchronized sprint/Jira lifecycle for DTM-19.

## Links
- Jira: DTM-19
- Sprint: agile/sprint_current.md
