# CAM-2026-03-09-GREP-GATES-V1

## Goal

Prevent new contour modules from dragging legacy or monster imports back into active runtime.

## Scope

- extend current guard scripts
- wire guards into CI workflows
- cover new contour scopes:
  - `src/telegram`
  - `src/commands`
  - `src/worker`
  - `src/observability`

## DoD

- active runtime paths are covered by guard scripts
- CI runs the relevant guards
- forbidden imports include legacy/core/pandas/GoogleSheetPlanner paths
