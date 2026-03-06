# Evidence — CAM-RENDER-INCIDENT-RCA-AND-GANTT-PARITY-V1

## Trust Gate
- source: `src/entrypoints/runtime/planner_runtime_entry.py`, `config/tables.yaml`, `src/services/calendar_runtime.py`
- last_verified_at: 2026-03-07
- verified_by: codex
- trust_level: high
- evidence:
  - render_v2 path previously targeted `sheet_info.get_sheet_name("tasks")` (`ТАБЛИЧКА`).
  - `target_sheet_name_prod_default` previously matched source spreadsheet.
  - legacy Gantt behavior is implemented in `TaskCalendarManager.all_tasks_to_sheet`.

## Incident Root Cause
1. render_v2 wrote to `tasks` sheet key (raw source table layout area).
2. In prod contour source/target spreadsheet names could resolve to the same book.
3. New render_v2 initially produced flat normalized view, not legacy Gantt.

## Applied safeguards
- Added render target validator (`src/render/target_guard.py`).
- Added hard block response for unsafe target:
  - `status=blocked`
  - `error.code=render_target_unsafe`
- Switched render_v2 target worksheet to `task_calendar` (`Задачи`).

## Expected smoke markers
- render_v2 response includes:
  - `target_worksheet: "Задачи"`
  - `render_applied: true|false`
  - `warnings: []` (or explicit reason)
- no writes to `ТАБЛИЧКА` from render_v2 contour.
