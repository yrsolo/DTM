# CAM-LEGACY-PLANNER-DELETE-V1

## Goal
Delete (or quarantine) planner world from standard runtime modes after consumers are migrated.

## Scope
- Remove `GoogleSheetPlanner` and planner dependency graph from standard runtime path.
- Keep optional explicit legacy modes only if strictly needed.

## Phases and Tasks
### P01 - Runtime map
- P01-T001: Map all runtime imports/usages of planner components.

### P02 - Consumer migration completion
- P02-T001: Ensure API/notify/render/group-query consumers are fully snapshot-based.

### P03 - Remove planner runtime usage
- P03-T001: Remove planner branch from standard modes.
- P03-T002: Move remaining legacy planner files under `src/legacy/` or remove.

### P04 - Config cleanup
- P04-T001: Remove planner-specific runtime switches from default config path.

## DoD
- Standard runtime modes do not import or execute planner world.
- Any remaining planner code is isolated to explicit legacy-only contour.
