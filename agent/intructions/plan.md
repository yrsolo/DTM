# plan.md — Legacy cut + Snapshot Engine hardening (revised)

Цель: полностью перевести runtime на Snapshot Engine (raw+prep+extra + query engine) и **выпилить legacy core/planner** из путей API/notify/render. Скорость уже норм — теперь доводим архитектуру до состояния “не может зарасти обратно”.

---

## Guiding rules (жёсткие)

1) **Никаких fallback в runtime на legacy**, кроме явного `mode=legacy_*` (выключено по умолчанию).
2) **Никаких импортов `core/*`, `planner/*`, `pandas`** в новых модулях.
3) Query/filter правила должны быть **в одном месте**: SnapshotQueryEngine.
4) `status` и `history` не путать:
   - `status` = нормализованный по цвету
   - `history` = текстовый статус из таблицы (free-form)
5) Если timing пустой — **start = today** (лучше `fetched_at_utc.date()`) — это нормальная эвристика для диаграмм.

---

# Priority order (очень важно)

1) **API v2**: убрать зависимость от `core.api_payload_v2` и pandas  
2) **Notify**: новый модуль напоминаний без legacy  
3) **Render**: новый модуль рендера без legacy  
4) **Убрать HTTP fallback**  
5) **Удалить planner world из runtime**  
6) Hardening: grep gates + CI checks

---

# CAM-LEGACY-CUT-API-V1 — API v2 полностью на Snapshot Engine без core/api_payload_v2

## Goal
`SnapshotQueryEngine.query_frontend_v2()` строит payload v2 напрямую из PrepSnapshot. Никаких `core.api_payload_v2`, `core.models.people.Person`, `pandas`.

## Phase P01 — Parity spec
- P01-T001: Зафиксировать contract parity (как сейчас):
  - filters: statuses / owner / window(intersects) / limit / include_people
  - tasks[].status и tasks[].history
  - milestones в ответе: если задача включена, milestones включаются все
- P01-T002: Добавить `docs/snapshot_engine/api_v2_parity.md` (коротко, 1–2 страницы).

## Phase P02 — Новый builder
- P02-T001: Создать `src/snapshot_engine/frontend_v2_payload_builder.py` (скелет уже дан).
- P02-T002: Реализовать сборку `tasks[]`:
  - `task.status <- sheet.status`
  - `task.history <- sheet.history`
  - `task.date.start/end` из `sheet.date_start/date_end`
  - `milestones` без фильтрации по окну
- P02-T003: Реализовать `entities` без Person/pandas:
  - people: из `owner_id` в выбранных задачах + минимальные поля (id,name) из `PrepSnapshot` (если есть)
  - enums: milestoneType только реально встречающиеся

## Phase P03 — Подключить builder в QueryEngine
- P03-T001: `SnapshotQueryEngine` принимает builder через ctor.
- P03-T002: Удалить legacy builder imports из snapshot_engine.

## Phase P04 — Тесты parity
- P04-T001: unit tests:
  - statuses фильтр
  - window intersects
  - limit
  - include_people false/true
  - history сохранён
- P04-T002: “golden” snapshot тест (маленький фиксированный PrepSnapshot → JSON).

## DoD
- grep: в `src/snapshot_engine/**` нет `import core`, `import pandas`, `Person`.
- API v2 работает от PrepCache.
- payload contract unchanged.

---

# CAM-NOTIFY-MODULE-V1 — Новый модуль напоминаний без legacy

## Goal
Новый notify контур: `SnapshotEngine -> ReminderUseCase -> ReminderFormatter -> TelegramSender`. Никаких `core/reminder`, planner, чтения Sheets.

## Phase P01 — Skeleton + wiring
- P01-T001: Добавить модули (скелеты уже даны):
  - `src/notify/model.py`
  - `src/notify/usecase.py`
  - `src/notify/formatter.py`
  - `src/notify/telegram_sender.py`
  - `src/notify/job.py`

## Phase P02 — Реализация usecase
- P02-T001: `ReminderUseCase.run(req)`:
  - вызывает `SnapshotEngine.reminders(query)` или напрямую `SnapshotQueryEngine.query_reminders`
  - окно по `date_start/date_end` intersects
  - статусы default: work/pre_done (если так принято)
  - группировка по owner_id
  - лимит на дизайнера (optional)

## Phase P03 — Форматирование и отправка
- P03-T001: Formatter делает сообщения “на человека”.
- P03-T002: Sender отправляет, без бизнес-логики.

## Phase P04 — Подключение в runtime
- P04-T001: добавить `mode=reminder_v2` (или заменить текущий reminder, если готовы).
- P04-T002: отрубить legacy reminder path (только legacy_mode если нужно).

## Tests
- P05-T001: unit tests на окно/статусы/группы.
- P05-T002: форматтер snapshot тест.

## DoD
- notify path не импортирует `core/*`.
- notify path не читает Sheets.

---

# CAM-RENDER-MODULE-V1 — Новый модуль рендера без legacy

## Goal
Рендер — это pure plan + infra writer: `SnapshotEngine -> RenderUseCase(build_plan) -> SheetsWriter.apply(plan)`. Никаких legacy sheet_renderer.

## Phase P01 — Skeleton + wiring
- P01-T001: добавить:
  - `src/render/model.py`
  - `src/render/usecase.py`
  - `src/render/sheets_adapter.py`
  - `src/render/job.py`

## Phase P02 — RenderUseCase.build_plan
- P02-T001: выбор задач делается через SnapshotQueryEngine (status/window/limit).
- P02-T002: build_plan делает:
  - список значений (RenderCell)
  - список форматов (RenderFormat)
  - ничего не пишет в Sheets.

## Phase P03 — SheetsWriter batching
- P03-T001: SheetsWriter делает batch updates:
  - values одним батчем
  - formats диапазонами где возможно
- P03-T002: smoke на маленьком диапазоне.

## DoD
- render path не импортирует `core/*`.
- render path не читает Sheets как источник данных.

---

# CAM-HTTP-FALLBACK-REMOVAL-V1 — Убрать fallback на legacy в HTTP

## Goal
API v2 всегда читает PrepCache. Если PrepSnapshot отсутствует → быстрый ответ “not ready” без сборки legacy payload.

## Tasks
- T001: Удалить ветки “если prep missing → build legacy”.
- T002: Вернуть 503/empty payload с `meta.reason=prep_not_ready`.
- T003: Evidence: cold start без prep → ответ < 200ms.

## DoD
- grep: в HTTP path нет `core.api_payload_v2`.
- нет вызовов main/planner из index.

---

# CAM-LEGACY-PLANNER-DELETE-V1 — Выпилить planner world из runtime

## Goal
Удалить (или вынести в `legacy/` и выключить):
- GoogleSheetPlanner
- build_planner_dependencies
- _apply_task_source_switches
- любые runtime mutation injection на repo

## Tasks
- T001: map runtime imports planner.
- T002: заменить все потребители на SnapshotEngine (API/notify/render/group_query).
- T003: переместить planner в `src/legacy/` (или удалить).
- T004: убрать конфиги/флаги, которые обслуживали planner, если не нужны.

## DoD
- стандартные режимы не импортируют planner.
- CI grep gate проходит.

---

# CAM-GREP-GATES-V1 — Anti-relapse защита

## Goal
Чтобы legacy не вернулся “по быстрому фиксу”.

## Tasks
- T001: добавить скрипт `scripts/check_no_legacy_imports.py` (или bash):
  - fail if found in `src/snapshot_engine`, `src/notify`, `src/render`, `src/entrypoints`:
    - `import core`
    - `from core`
    - `import pandas`
    - `GoogleSheetPlanner`
    - `build_planner_dependencies`
- T002: подключить в CI (pre-commit или GitHub Actions).
- T003: добавить в `AGENTS.md` правило: новый код не может импортировать legacy.

## DoD
- PR не проходит, если кто-то добавил legacy import.

---

# Notes / Optional track

## CAM-EXTRA-STORE-SCALE-V1 (optional, when enrichment grows)
Если extra станет много (docs по большинству задач), текущая модель “1 объект на задачу” может стать узким местом.
Решение:
- single-blob extra map (`extra/all.json`) или index+selective fetch
- + нормальный orphan lifecycle (`list_ids`).

---

## Final expected state (definition)
- Единственный источник чтения для потребителей: PrepCache + SnapshotQueryEngine.
- Legacy core/planner не участвуют в runtime.
- Новые notify/render модули независимы и тестируемы.
- Никаких монстро-контекстов и callback wiring.