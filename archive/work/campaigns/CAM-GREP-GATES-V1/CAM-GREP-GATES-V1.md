# CAM-GREP-GATES-V1

## Goal
Prevent re-introducing legacy imports into new runtime contours.

## Scope
- Add guard script and CI check for forbidden imports/usages.
- Enforce for snapshot/notify/render/entrypoints boundaries.

## Phases and Tasks
### P01 - Guard script
- P01-T001: Add `scripts/check_no_legacy_imports.py`.
- P01-T002: Enforce forbidden patterns in target paths:
  - `import core`, `from core`
  - `import pandas`
  - `GoogleSheetPlanner`
  - `build_planner_dependencies`

### P02 - CI integration
- P02-T001: Add check to CI workflow.
- P02-T002: Ensure non-zero exit on violation.

### P03 - Policy sync
- P03-T001: Sync AGENTS/runtime docs with guard expectations.

## DoD
- CI fails when forbidden legacy imports appear in target contours.
