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

## 2026-03-07 parity tune (post-incident follow-up)
- source: `src/render/usecase.py`, `src/services/calendar_runtime.py`
- verified_by: codex
- trust_level: high
- fixes:
  - aligned timeline window anchor to legacy (`pd.Timestamp.now().floor("D")` based).
  - changed timeline loop to legacy half-open behavior (`day < end`).
  - restored continuous gantt band fill across whole task range (no skip on empty stage day).
  - preserved stage labels in task cells, including `ответ клиента` path (no day drop).
- test evidence:
  - `python -m unittest tests.render.test_render_v2 -v` -> OK
  - `python -m unittest tests.render.test_target_guard -v` -> OK
- local runtime evidence:
  - `mode=sync-only force_refresh=true` completed and produced snapshot update.
  - `mode=render_v2 force_refresh=true` ->
    - `target_spreadsheet=Спонсорские ТНТ ТЕСТ`
    - `target_worksheet=Задачи`
    - `render_applied=true`
    - `rows_written=20`
    - `cells_written=1540`
    - `duration_ms=11200`

## 2026-03-07 designers sheet parity extension
- Implemented snapshot-based designers render use-case: `src/render/designers_usecase.py`.
- Wired `render_v2` runtime to render both worksheets in one run:
  - `Задачи` (task calendar)
  - `Дизайнеры` (designer columns)
- Runtime response now includes per-target section `targets.task_calendar` + `targets.designers`.
- Verification:
  - `python -m unittest tests.render.test_designers_render_v2 -v` -> OK
  - local `mode=render_v2` run ->
    - `target_spreadsheet=Спонсорские ТНТ ТЕСТ`
    - `targets.designers.target_worksheet=Дизайнеры`
    - `targets.designers.render_applied=true`

## 2026-03-07 legacy calendar disable
- Runtime path no longer calls `planner.designer_task_to_calendar()`.
- Added log marker: `calendar_render=disabled` in planner use-case sync branch.
- Regression test added: `tests/services/test_planner_runtime_usecase.py`.
