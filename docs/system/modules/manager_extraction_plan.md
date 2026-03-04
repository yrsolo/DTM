# Manager Extraction Plan (Core Cleanup)

## Goal
Move service/render orchestration from `core/manager.py` to adapter/service boundaries while keeping scheduling logic stable.

## Current mixed areas in `core/manager.py`
- Domain/application logic:
  - task timing aggregation
  - calendar row shaping
  - grouping/sorting rules
- Infra logic:
  - direct renderer coupling via `ServiceSheetRenderAdapter`
  - sheet-oriented managers (`CalendarManager`, `TaskCalendarManager`) with write-side behavior

## Atomic extraction sequence
1. Extract pure timing/calendar transformation helpers into `core/calendar_policy.py`.
2. Move sheet write managers to `src/services/calendar_runtime.py`:
   - `CalendarManager`
   - `TaskCalendarManager`
3. Keep `TaskTimingProcessor` in core (domain) and switch callers to new service module.
4. Leave compatibility re-exports in `core/manager.py` during migration.
5. Move remaining renderer-specific defaults from core to `src/adapters/google_sheets_renderer.py` or service bootstrap.

## Safety checks
- `python -m py_compile core/manager.py src/services/calendar_runtime.py`
- `python -m unittest tests.services.test_pipeline_runtime -v`
- verify no new `utils.service` imports in `core/**`.
