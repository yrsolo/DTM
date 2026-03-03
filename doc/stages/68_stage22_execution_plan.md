# Stage 22 Execution Plan

## Objective
Unify production data-consumption paths so Frontend API, Sheet Render, and Notifications read via one shared DB query contract and filtering semantics.

## Baseline
- Stage 22 estimate baseline: 6 tasks.
- Dynamic tracking rule: after each completed task, update `Done` and `Remaining` in `agile/sprint_current.md`.
- Current counter after kickoff: done `0`, remaining `6`.

## Stage 22 slices (initial)
1. `DTM-228`: Stage 22 kickoff and bounded queue.
2. `DTM-229`: unified DB query contract adapter for API/render/notify.
3. `DTM-230`: source-policy cleanup (`READMODEL_SOURCE`/`NOTIFY_SOURCE`/`RENDER_SOURCE`) with one consumer matrix.
4. `DTM-231`: production runbook for `db_migrate`, forced refresh, rollback and safety gates.
5. `DTM-232`: tri-block smoke suite from single query contract source.
6. `DTM-233`: Stage 22 closeout and Stage 23 handoff package.

## Delivery rules
- WIP stays 1 active execution task.
- Jira is optional; local tracking in `agile/sprint_current.md` + `agile/tasks/*.md` is valid control plane.
- Every completed task must include runnable evidence (tests/smoke/log artifact).

## Exit criteria
- API/render/notify query logic is centralized (no duplicate filter branches).
- One source-of-truth contract defines statuses/designer/time-window/milestone filtering.
- Smoke evidence confirms parity across the three product blocks.
- Stage 22 closeout package and Stage 23 proposal are published.
