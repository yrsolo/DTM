# CAM-2026-03-22-RENDERING-EXECUTION-SURFACE-V1 Plan

## Trust Gate
- source: `src/contexts/rendering/public.py`, `src/contexts/rendering/internal/job_runners.py`, `src/platform/runtime/queue_bootstrap.py`
- last_verified_at: 2026-03-22
- verified_by: Codex
- evidence:
  - `rg -n "from src\\.contexts\\.rendering\\.public import|get_snapshot_read_api\\(|get_timeline_usecase\\(|get_designers_usecase\\(|get_window\\(|get_request\\(|get_writer\\(|get_render_job\\(" src tests`
  - direct reads of active rendering runtime files
- trust_level: high
- notes:
  - The helper catalog in `rendering.public` is still a live execution seam for rendering job runners.

## Phases

### P01 - Canonical Rendering Execution Surface
- `CAM-2026-03-22-RENDERING-EXECUTION-SURFACE-V1-P01-T001` Add one application-owned rendering execution API for timeline/designers job assembly.
- `CAM-2026-03-22-RENDERING-EXECUTION-SURFACE-V1-P01-T002` Repoint rendering job runners to that execution API instead of helper-by-helper public imports.
- `CAM-2026-03-22-RENDERING-EXECUTION-SURFACE-V1-P01-T003` Shrink `rendering.public` to canonical execution surface exports plus queue command handlers.

### P02 - Verification And Tracking
- `CAM-2026-03-22-RENDERING-EXECUTION-SURFACE-V1-P02-T001` Run the targeted rendering/planner/guardrail test contour.
- `CAM-2026-03-22-RENDERING-EXECUTION-SURFACE-V1-P02-T002` Close out local tracking and archive the completed campaign record.
