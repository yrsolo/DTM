```md
# Инструкции агенту: как пользоваться skeleton Snapshot Engine

Этот репозиторий содержит **skeleton** (черновики модулей без реализаций) для новой чистой архитектуры “две витрины + enrichment”, чтобы уйти от planner/legacy и монстро-контекстов.

Цель: внедрить новый контур **не переписывая всё**, а через “strangler”: сначала новый модуль, потом переключение API/notify/render на него.

---

## 0) Что именно лежит в skeleton

Папки/файлы:

- `docs/snapshot_engine/*` — документация новой архитектуры и миграции
- `src/snapshot_engine/*` — типы/интерфейсы/фасад/джоб/квери-движок (без реализаций)
- `src/snapshot_engine/stores/*` — заготовки хранилищ (YDB/S3) без реализаций
- `src/entrypoints_adapters/*` — заготовки адаптеров entrypoint→engine (API/notify) без реализаций

Важно: **реализаций нет** — их надо написать, но строго сохраняя границы модулей и контракты.

---

## 1) Основные идеи (которые нельзя нарушать)

### 1.1 Два кэша + enrichment
- **RawCache**: нормализованные задачи из Sheets (истина “из таблицы”), keyed by `task_id` (UUID).
- **ExtraStore**: дополнительная инфа по задаче, которую пользователь добавит через сайт (docs/links/notes/artifacts). Не приходит из Sheets.
- **PrepCache**: витрина для чтения (TaskView = merge(sheet_task + extra) + indexes).

### 1.2 Один модуль запросов к слепку
И API, и нотификатор, и рендер должны использовать **один** модуль:
- `SnapshotQueryEngine`

Он получает `PrepSnapshot` и query DTO и возвращает результат.

### 1.3 Status vs History (важно!)
В задаче два разных поля:
- `TaskSheet.status` — нормализованный статус по цвету (work/pre_done/wait/done)
- `TaskSheet.history` — сырой текстовый статус/история из таблицы (free-form), только для отображения
Фильтрация по статусам делается по `status`, не по `history`.

---

## 2) Какие части надо реализовать (в правильном порядке)

### Шаг A — Реализовать хранилища (stores)
Нужно выбрать где реально храним:
- На старте можно оставить **YDB** как KV/Blob-хранилище (самое просто, уже есть креды).
- Позже можно заменить Raw/Prep на S3.

Минимально нужно реализовать:
1) `YdbRawCache.get/put`
2) `YdbPrepCache.get/put`
3) `YdbExtraStore.get_many/upsert/mark_orphaned`

Примечание:
- RawCache и PrepCache можно хранить как **один JSON blob** (1 row) — это целевой быстрый режим.
- ExtraStore — keyed by task_id (таблица).

### Шаг B — Реализовать SheetsSource + Hasher + Normalizer
- `SheetsSource.fetch_snapshot()` должен читать values+colors (как сейчас в проекте).
- `Hasher.hash_sheet_snapshot()` должен стабильно хэшировать values+colors (чтобы detect changes).
- `Normalizer.normalize()` должен превратить snapshot в `RawSnapshot`:
  - заполнить `TaskSheet.status` (по цвету)
  - заполнить `TaskSheet.history` (текстовый статус)
  - распарсить milestones и гарантировать минимум `start`
  - посчитать `date_start/date_end` агрегаты

### Шаг C — Реализовать PrepBuilder
`PrepBuilder.build(raw)` должен:
1) прочитать extra для task_ids из `extra_store.get_many()`
2) выявить orphan ids (те, кто был в extra, но нет в raw) и пометить orphaned (не удалять)
3) собрать `tasks_by_id: Dict[task_id, TaskView(sheet, extra)]`
4) построить `indexes`:
   - by_status на основе `TaskView.sheet.status`
   - by_owner на основе `TaskView.sheet.owner_id` (если нужно)
5) вернуть `PrepSnapshot(built_at, raw_source_hash, tasks_by_id, indexes)`

### Шаг D — Реализовать UpdateJob
`UpdateJob.run(force=False)`:
1) fetch snapshot
2) compute source_hash
3) если hash не изменился и force=False → вернуть changed=False
4) normalize → RawSnapshot
5) RawCache.put(raw)
6) prep = PrepBuilder.build(raw)
7) PrepCache.put(prep)
8) вернуть UpdateResult

### Шаг E — Реализовать SnapshotQueryEngine
Реализовать минимум:
- `select_by_status` (по `TaskView.sheet.status`)
- `filter_by_owner`
- `filter_by_window` (по `TaskView.sheet.date_start/date_end`, intersects)
- `apply_limit`
- `query_frontend_v2` → возвращает payload, совместимый с текущим API v2
- `query_reminders` → grouped by owner_id, с применением окна/статусов/лимитов

---

## 3) Как подключить это к текущему проекту (strangler)

### 3.1 Добавить новый режим update (без замены старого)
- Создать новый job/handler: `snapshot_update`
- Он вызывает `UpdateJob.run()`
- Пока не трогаем старый sync pipeline, просто запускаем этот update по расписанию отдельно.

### 3.2 Переключить API v2 на чтение PrepCache
- В HTTP обработчике `/api/v2/frontend`:
  - создать `SnapshotEngine` через bootstrap (raw_cache/prep_cache/query_engine)
  - собрать `FrontendV2Query` из query params
  - вернуть `engine.frontend_v2(query).data`
- Контракт API v2 не меняется.

### 3.3 Переключить notifier на чтение PrepCache
- Нотификатор должен использовать `engine.reminders(query)` и не читать Sheets.

### 3.4 Legacy/planner оставить временно
- На первом этапе не удаляем старый код.
- Удаление/чистка будет отдельной кампанией после стабилизации.

---

## 4) Правила качества (чтобы не превратилось в монстров)

Запрещено:
- делать фабрики “передаю 20 функций параметрами”
- делать dataclass Context с функциями/лямбдами
- читать env внутри сервисов (только bootstrap/loader)

Обязательно:
- все зависимости берутся через `AppContext` или явно через конструкторы классов
- один `SnapshotQueryEngine` для всех потребителей
- `status` и `history` не путать

---

## 5) Минимальные тесты (обязательно)
1) `Normalizer`:
- гарантирует `milestones` не пустые (start добавлен)
- корректно заполняет `status` и `history`

2) `PrepBuilder`:
- indexes.by_status строится по `status`
- `history` не влияет на индексы

3) `QueryEngine`:
- window intersects по date_start/date_end
- API v2 payload не меняет контракт

---

## 6) Definition of Done для внедрения skeleton
- UpdateJob по расписанию строит RawCache и PrepCache.
- API v2 отдаёт данные из PrepCache через SnapshotEngine и сохраняет контракт.
- Нотификатор использует SnapshotEngine.
- Никакой зависимостей от planner для этих путей.
```
