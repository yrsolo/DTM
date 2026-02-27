# DTM-27 - Stage 3 render contract parity for calendar header/date cells

## Context
- `DTM-26` вынес write-path `CalendarManager` за `SheetRenderAdapter` boundary.
- Внутри `CalendarManager` часть cell payload still assembled as ad-hoc dict blocks.
- Jira issue: `DTM-27` (status: `Gotovo`).

## Goal
- Нормализовать header/date/body payload assembly в `CalendarManager` через shared render contract helpers.
- Сохранить output parity.

## Non-goals
- Без визуальных изменений листа `Календарь`.
- Без расширения scope на `TaskManager` и reminder path.
- Без изменений в `GoogleSheetsService` internals.

## Plan
1. Вынести helper methods для calendar cell payload assembly.
2. Перевести `write_calendar_to_sheet` на helper methods.
3. Проверить parity через smoke dry-run.
4. Синхронизировать Jira/sprint/docs.

## Checklist (DoD)
- [x] Calendar header/date/body payload creation normalized via helpers.
- [x] Shared render contract usage preserved.
- [x] Smoke checks pass (`py_compile`, `local_run.py --mode sync-only --dry-run`).
- [x] Sprint/docs/Jira synchronized.

## Work log
- 2026-02-27: Task moved to `V rabote` after `DTM-26` completion.
- 2026-02-27: CalendarManager payload assembly normalized through helper methods (`_build_calendar_header_cell`, `_build_calendar_date_cell`, `_build_calendar_stage_cell`) over shared `RenderCell`.
- 2026-02-27: Smoke passed: `python -m py_compile core/manager.py core/bootstrap.py core/sheet_renderer.py core/adapters.py`, `python local_run.py --mode sync-only --dry-run`.
- 2026-02-27: Jira evidence comment added; issue transitioned to `Gotovo`.

## Links
- `core/manager.py`
- `core/render_contracts.py`
- `agile/sprint_current.md`
