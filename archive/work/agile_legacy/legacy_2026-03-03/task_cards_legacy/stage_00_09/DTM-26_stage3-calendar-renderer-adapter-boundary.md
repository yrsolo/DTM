# DTM-26 - Stage 3 calendar renderer adapter boundary extraction

## Context
- `DTM-25` завершил adapter boundary для `TaskCalendarManager`.
- `CalendarManager` все еще напрямую использует `GoogleSheetsService` для write-операций.
- Jira issue: `DTM-26` (status: `Gotovo`).

## Goal
- Вынести write-path `CalendarManager` за `SheetRenderAdapter` boundary.
- Подключить adapter через bootstrap dependency injection.
- Сохранить поведение вывода без изменений.

## Non-goals
- Без функционального редизайна календарного листа.
- Без переписывания `GoogleSheetsService`.
- Без изменений reminder-потока.

## Plan
1. Добавить/использовать adapter wiring для `CalendarManager`.
2. Перевести write path в `CalendarManager` на adapter методы.
3. Подключить renderer dependency в `core/bootstrap.py`.
4. Прогнать smoke-check и синхронизировать Jira/docs/sprint.

## Checklist (DoD)
- [x] `CalendarManager` использует `SheetRenderAdapter` для write-операций.
- [x] Adapter dependency подключен в bootstrap.
- [x] Smoke checks pass (`py_compile`, `local_run.py --mode sync-only --dry-run`).
- [x] `agile/sprint_current.md` / `agile/context_registry.md` обновлены.
- [x] Jira evidence comment added and issue transitioned per lifecycle.

## Work log
- 2026-02-27: Task created in Jira and moved to `V rabote`.
- 2026-02-27: Freshness check completed on `CalendarManager` write hotspots and bootstrap wiring.
- 2026-02-27: CalendarManager write path switched to `SheetRenderAdapter`; bootstrap DI updated with calendar renderer dependency.
- 2026-02-27: Smoke passed: `python -m py_compile core/manager.py core/bootstrap.py core/sheet_renderer.py core/adapters.py`, `python local_run.py --mode sync-only --dry-run`.
- 2026-02-27: Jira evidence comment added; issue transitioned to `Gotovo`.

## Links
- `core/manager.py`
- `core/bootstrap.py`
- `core/sheet_renderer.py`
- `agile/sprint_current.md`
