# CAM-RENDER-INCIDENT-RCA-AND-GANTT-PARITY-V1

## Goal
Исключить повтор инцидента записи в исходный лист `ТАБЛИЧКА`, вернуть render_v2 к ожидаемому Gantt-формату 1:1 и закрепить безопасный target (`Задачи`).

## Scope
- safety gate для render target;
- переключение render_v2 на `task_calendar` (`Задачи`);
- перенос Gantt-алгоритма из legacy `TaskCalendarManager.all_tasks_to_sheet` в `src/render/*`;
- обновление тестов и системной документации.

## Non-goals
- изменение API v2 snapshot/query контрактов;
- удаление legacy planner-кода;
- redesign внешнего вида Gantt (нужна parity, не новый UX).

## Phases
1. P01: RCA evidence и фиксация причины.
2. P02: fail-safe target guard (`render_target_unsafe`).
3. P03: target switch (`tasks` -> `task_calendar`).
4. P04: Gantt parity в новом render-контуре.
5. P05: source/target safety rules в config-loader.
6. P06: tests + docs + smoke.

## DoD
- render_v2 никогда не пишет в `ТАБЛИЧКА`;
- unsafe target блокируется с кодом `render_target_unsafe`;
- render_v2 пишет в `Задачи` и строит Gantt-представление;
- тесты `tests/render/*` и runtime/api smoke зелёные;
- runbook/dataflow/entrypoints docs отражают новое правило безопасности.
