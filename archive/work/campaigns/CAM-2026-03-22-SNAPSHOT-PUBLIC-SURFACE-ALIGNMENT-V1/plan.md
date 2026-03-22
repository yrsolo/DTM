# CAM-2026-03-22-SNAPSHOT-PUBLIC-SURFACE-ALIGNMENT-V1 Plan

## Trust Gate
- source: `src/contexts/snapshot/public.py`, `src/contexts/snapshot/module.py`, `src/platform/runtime/queue_bootstrap.py`
- last_verified_at: 2026-03-22
- verified_by: Codex
- evidence:
  - `rg -n "from src\\.contexts\\.snapshot\\.public import|import src\\.contexts\\.snapshot\\.public|get_read_capability\\(|get_attachment_capability\\(|get_query_capability\\(|get_update_capability\\(" src tests`
  - direct reads of active snapshot module and queue bootstrap files
- trust_level: high
- notes:
  - `snapshot.public` is no longer carrying significant live traffic, but its `*capability` grammar still misstates the now-canonical module API shape.

## Phases

### P01 - Public Surface Alignment
- `CAM-2026-03-22-SNAPSHOT-PUBLIC-SURFACE-ALIGNMENT-V1-P01-T001` Replace the leftover `*capability` public exports with canonical API names aligned to `snapshot.module`.
- `CAM-2026-03-22-SNAPSHOT-PUBLIC-SURFACE-ALIGNMENT-V1-P01-T002` Keep queue command handlers intact while removing the leftover `get_public_api` facade.

### P02 - Verification And Tracking
- `CAM-2026-03-22-SNAPSHOT-PUBLIC-SURFACE-ALIGNMENT-V1-P02-T001` Run the targeted snapshot/guardrail/import-safety contour.
- `CAM-2026-03-22-SNAPSHOT-PUBLIC-SURFACE-ALIGNMENT-V1-P02-T002` Close out local tracking and archive the completed campaign record.
