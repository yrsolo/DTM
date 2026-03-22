# CAM-2026-03-22-REMINDERS-DELIVERY-SURFACE-V1 Plan

## Trust Gate
- source: `src/contexts/reminders/public.py`, `src/contexts/reminders/internal/job_runner.py`, `src/entrypoints/runtime/planner_runtime_entry.py`
- last_verified_at: 2026-03-22
- verified_by: Codex
- evidence:
  - `rg -n "get_snapshot_read_api|get_usecase|get_formatter|get_sender|get_enhancer|get_today_in_runtime_timezone|get_job_runner|make_reminder_request" src tests`
  - direct reads of active reminders and planner runtime files
- trust_level: high
- notes:
  - The helper catalog in `reminders.public` is still part of the live runtime path, not dead compatibility residue.

## Phases

### P01 - Canonical Delivery Surface
- `CAM-2026-03-22-REMINDERS-DELIVERY-SURFACE-V1-P01-T001` Add one application-owned reminder delivery API that assembles the current live reminder scenario.
- `CAM-2026-03-22-REMINDERS-DELIVERY-SURFACE-V1-P01-T002` Repoint planner runtime and queue execution to that delivery API instead of helper-by-helper public imports.
- `CAM-2026-03-22-REMINDERS-DELIVERY-SURFACE-V1-P01-T003` Shrink `reminders.public` to canonical surface exports only and keep queue command handlers intact.

### P02 - Verification And Tracking
- `CAM-2026-03-22-REMINDERS-DELIVERY-SURFACE-V1-P02-T001` Run the targeted reminders/planner/guardrail test contour.
- `CAM-2026-03-22-REMINDERS-DELIVERY-SURFACE-V1-P02-T002` Close out local tracking and archive the completed campaign record.
