# CAM-PIPELINE-CLEAN-SKELETON-V1 — Чистый “скелет” пайплайна (после CONFIG-V0)

## Goal
Сделать основной пайплайн чистым и линейным: минимальные if-ы, все политики/выборы — в bootstrap, ошибки — через единый boundary.

## Problem statement
Сейчас `index.py` и `main.py` содержат оркестрацию и условия/флаги. Из-за этого:
- сложно читать,
- сложно тестировать,
- новые фичи добавляются через новые if-ветки.

## Scope
1) Ввести “чистые use-cases” (application services) с фиксированным контрактом:
- `SyncFromSheets.run(ctx) -> SyncResult`
- `BuildFrontendReadmodel.run(ctx) -> BuildResult`
- `RenderSheets.run(ctx) -> RenderResult`
- `SendMorningReminders.run(ctx) -> NotifyResult`
2) Ввести единый Job orchestration:
- `TimerJob.run(ctx)` вызывает use-cases линейно.
3) Вынести policy selection из кода use-cases:
- выбор источника чтения/записи делается в bootstrap (инъекция реализации).

## Non-goals
- Не переписывать domain-алгоритмы.
- Не менять контракты API v2.

## Deliverables
- `src/services/usecases/*.py` (или аналогичная структура)
- `src/entrypoints/jobs/timer_job.py`
- `src/app/context.py` (Ctx: cfg + deps)
- Док: `docs/system/dataflow.md` обновить “как это вызывается”.

## Hard rules
- В use-cases не должно быть `os.getenv`, `constants`, `if cfg.mode == ...` (режимы — только в entrypoints).
- В use-cases допускаются только:
  - линейные шаги,
  - decision “делать следующий шаг или нет” по результату (did_change/ttl fresh).

## Phases & tasks
### P01 — Context + use-case interfaces
- T001: Ввести `AppContext` (cfg + repos + adapters + clock + logger).
- T002: Создать интерфейсные классы/протоколы для зависимостей (если нужно).

### P02 — TimerJob
- T001: Реализовать `TimerJob.run(ctx)` как 10–20 строк:
  - sync
  - build readmodel (if needed)
  - render (if enabled)
  - notify (if enabled)
- T002: Вся логика “enabled” приходит из cfg и реализована как “подключён сервис или NoOp”.

### P03 — Error boundary
- T001: Ввести исключения: `TransientError`, `PermanentError`, `UserError`.
- T002: Только entrypoints переводят их в exit-code/HTTP status.
- T003: Внутри сервисов нет HTTP/exit решений.

## DoD
- `TimerJob` читается как сценарий.
- Use-cases тестируются без entrypoints.
- Новая фича добавляется новым use-case или новой policy реализацией, а не 20 if-ами.