# CAM-2026-03-21-REPO-SURFACE-FINALIZATION-V1 Plan

## Goal

Close the remaining agreed repo-surface polish tasks:
- keep owner-provided input material under a role-true shelf in `agent/`,
- finish the last umbrella test-root cleanup,
- rewrite the root `README.md` in Russian with clearer architecture positioning,
- trim stale wording from active `work/` tracking.

## Phases

### P01 - Owner input shelf
- `CAM-2026-03-21-REPO-SURFACE-FINALIZATION-V1-P01-T001` keep owner input material under a role-true `agent/owner_inputs` folder.
- `CAM-2026-03-21-REPO-SURFACE-FINALIZATION-V1-P01-T002` update active references and guidance so files there are treated as owner input only, never as direct execution tracking.

### P02 - Test contour cleanup
- `CAM-2026-03-21-REPO-SURFACE-FINALIZATION-V1-P02-T001` redistribute `tests/api/*` into role-true homes under `tests/contexts`, `tests/entrypoints`, and `tests/platform` where appropriate.
- `CAM-2026-03-21-REPO-SURFACE-FINALIZATION-V1-P02-T002` keep snapshot JSON fixtures under a clearer fixture home instead of the old umbrella snapshot shelf.
- `CAM-2026-03-21-REPO-SURFACE-FINALIZATION-V1-P02-T003` remove stale `__pycache__` leftovers from the touched test contour.

### P03 - Root narrative and tracking
- `CAM-2026-03-21-REPO-SURFACE-FINALIZATION-V1-P03-T001` rewrite root `README.md` in Russian.
- `CAM-2026-03-21-REPO-SURFACE-FINALIZATION-V1-P03-T002` replace opaque architecture tags with clearer architecture-language plus explicit technology tags.
- `CAM-2026-03-21-REPO-SURFACE-FINALIZATION-V1-P03-T003` trim stale backlog/task wording that still reads like a historical dump instead of current state.
