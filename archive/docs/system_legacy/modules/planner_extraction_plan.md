# Planner Extraction Plan (Core Cleanup)

## Goal
Move orchestration facade from `core/planner.py` to `src/services/*` while preserving entrypoint behavior.

## Current mixed areas in `core/planner.py`
- Application orchestration:
  - dependency assembly via `build_planner_dependencies`
  - sequence of task/calendar/reminder jobs
  - quality report aggregation
- Transitional compatibility:
  - stores runtime-facing attributes for legacy callers

## Atomic extraction sequence
1. Create `src/services/planner_runtime.py` and move `GoogleSheetPlanner` implementation there unchanged.
2. Keep `core/planner.py` as compatibility shim re-exporting `GoogleSheetPlanner` and `build_reminder_sli_summary`.
3. Update non-legacy imports (`main.py`, other runtime modules) to `src/services/planner_runtime.py`.
4. Keep constructor signature unchanged during shim phase.
5. After stability window, remove legacy-only attributes from planner state if no caller requires them.

## Risk controls
- Preserve public methods and names: `task_to_table`, `designer_task_to_calendar`, `task_to_calendar`, `send_reminders`, `build_quality_report`.
- Do not alter report counter keys in same change as file move.
- Keep dependency injection path (`dependencies` parameter) intact.

## Safety checks
- `python -m py_compile core/planner.py src/services/planner_runtime.py main.py index.py`
- `python -m unittest tests.services.test_pipeline_runtime -v`
