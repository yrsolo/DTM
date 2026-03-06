```md
# CAM-SNAPSHOT-ENGINE-V1 — Внедрение Snapshot Engine (две витрины + enrichment)

## Goal
Внедрить новый чистый контур хранения и выборок:
**Sheets → Normalize → RawCache → Merge Extra → PrepCache → QueryEngine → (API/Notify/Render)**

- RawCache и PrepCache хранятся как JSON blob (1 row/file), ExtraStore — keyed by task_id.
- API v2 и notifier читают только PrepCache и используют единый SnapshotQueryEngine.
- Сохранить приёмственность API v2 контракта (meta+filters+summary+entities+tasks).

## Non-goals
- Не удалять legacy/planner код в этой кампании (только переключить чтение на новый контур).
- Не оптимизировать производительность “в ноль” (сначала правильность и ясные границы).
- Не вводить LLM обработку внутрь update (LLM enrichment — отдельная кампания).

## DoD
- UpdateJob по расписанию строит RawCache и PrepCache.
- API v2 `/api/v2/frontend` отвечает из PrepCache (без Sheets/YDB operational).
- Notifier берет данные из PrepCache и не читает Sheets.
- `status` (нормализованный) и `history` (сырой текст) не перепутаны.
- Есть минимальные тесты и evidence.

---

## PHASE P01 — Storage contracts and minimal schema

### CAM-SNAPSHOT-ENGINE-V1-P01-T001 — Finalize snapshot schema (Raw/Prep/Extra)
- Утвердить поля:
  - TaskSheet.status (цвет→нормализованный)
  - TaskSheet.history (сырой текст)
  - TaskSheet.date_start/date_end (агрегаты для window)
- Утвердить структуру PrepSnapshot:
  - tasks_by_id: task_id -> TaskView(sheet, extra)
  - indexes.by_status: status -> [task_id]
  - indexes.by_owner: owner_id -> [task_id]
- Зафиксировать в `docs/snapshot_engine/architecture.md`.

### CAM-SNAPSHOT-ENGINE-V1-P01-T002 — Define storage layout
- Решить где лежат blob snapshots на первом этапе:
  - вариант A: YDB single-row tables (`dtm_raw_snapshot`, `dtm_prep_snapshot`)
  - вариант B: S3 objects (`raw.json`, `prep.json`) — позже
- Для V1: выбрать A (YDB), чтобы быстрее внедрить без новой инфраструктуры.
- Зафиксировать в `docs/snapshot_engine/migration_plan.md`.

### CAM-SNAPSHOT-ENGINE-V1-P01-T003 — Create DB tables for V1 (if using YDB)
- Добавить DDL (или ensure_tables) для:
  - `dtm_raw_snapshot (id, payload_json, source_hash, fetched_at_utc)`
  - `dtm_prep_snapshot (id, payload_json, raw_source_hash, built_at_utc)`
  - `dtm_task_extra (task_id, payload_json, orphaned, updated_at_utc)`
- Primary key: id="default" для raw/prep; task_id для extra.

---

## PHASE P02 — Implement stores (YDB) and serializers

### CAM-SNAPSHOT-ENGINE-V1-P02-T001 — Implement JSON serialization helpers
- Ввести модуль:
  - `src/snapshot_engine/serialization.py`
- Функции:
  - `raw_to_json(raw: RawSnapshot) -> str`
  - `raw_from_json(s: str) -> RawSnapshot`
  - `prep_to_json(prep: PrepSnapshot) -> str`
  - `prep_from_json(s: str) -> PrepSnapshot`
  - `extra_to_json(extra: TaskExtra) -> str`
  - `extra_from_json(s: str) -> TaskExtra`
- Принцип: stable JSON encoding (isoformat for dates/datetimes).

### CAM-SNAPSHOT-ENGINE-V1-P02-T002 — Implement YdbRawCache/YdbPrepCache
- Реализовать:
  - `YdbRawCache.get/put`
  - `YdbPrepCache.get/put`
- Требование: один YdbClient/Driver per run (не создавать клиентов внутри методов).

### CAM-SNAPSHOT-ENGINE-V1-P02-T003 — Implement YdbExtraStore
- Реализовать:
  - `get_many(task_ids)`
  - `upsert(extra)`
  - `mark_orphaned(task_id, orphaned=True)`
- Политика: orphaned не удалять.

### CAM-SNAPSHOT-ENGINE-V1-P02-T004 — Unit tests for serialization + stores (smoke)
- Тест roundtrip для RawSnapshot/PrepSnapshot/TaskExtra.
- Мок/интеграционный тест: put/get возвращает эквивалент.

---

## PHASE P03 — SheetsSource + Hasher + Normalizer

### CAM-SNAPSHOT-ENGINE-V1-P03-T001 — Implement SheetsSource.fetch_snapshot
- Использовать существующий Sheets adapter.
- Возвращать `SheetSnapshot(values+colors)`.

### CAM-SNAPSHOT-ENGINE-V1-P03-T002 — Implement Hasher.hash_sheet_snapshot
- В hash входит values + colors.
- Stable json hashing: sorted keys, stable separators, normalized None/"" rules.

### CAM-SNAPSHOT-ENGINE-V1-P03-T003 — Implement Normalizer.normalize
- Преобразовать snapshot → tasks_by_id[task_id] = TaskSheet(...)
- Заполнить:
  - `status` (нормализованный по цвету)
  - `history` (сырой текстовый статус из колонки)
  - milestones (минимум start)
  - date_start/date_end (агрегаты)
- Проверка: milestones не пустые.

### CAM-SNAPSHOT-ENGINE-V1-P03-T004 — Unit tests for normalization invariants
- start milestone is added when missing
- status/history both present and distinct
- window intersects uses date_start/date_end

---

## PHASE P04 — PrepBuilder (merge enrichment + indexes)

### CAM-SNAPSHOT-ENGINE-V1-P04-T001 — Implement PrepBuilder.build
- Load extras: `extra_store.get_many(raw.task_ids)`
- Merge: TaskView(sheet, extra)
- Mark orphaned extras for deleted tasks:
  - deleted = extras.keys - raw.task_ids
  - mark_orphaned(deleted)
- Build indexes:
  - by_status uses `sheet.status`
  - by_owner uses `sheet.owner_id`

### CAM-SNAPSHOT-ENGINE-V1-P04-T002 — Tests for PrepBuilder indexes and orphan policy
- history does not affect indexes
- orphan marking works, but extras not deleted

---

## PHASE P05 — UpdateJob (scheduled refresh)

### CAM-SNAPSHOT-ENGINE-V1-P05-T001 — Implement UpdateJob.run
- Fetch snapshot
- Compute source_hash
- If unchanged and not force → changed=False (no writes)
- Else normalize → RawCache.put
- Build prep → PrepCache.put
- Return UpdateResult

### CAM-SNAPSHOT-ENGINE-V1-P05-T002 — Add logs/metrics (minimal)
- t_fetch_ms, t_normalize_ms, t_build_prep_ms, t_put_raw_ms, t_put_prep_ms
- changed flag and source_hash

### CAM-SNAPSHOT-ENGINE-V1-P05-T003 — Smoke run locally
- Run update once and verify caches exist

---

## PHASE P06 — SnapshotQueryEngine + API v2 parity

### CAM-SNAPSHOT-ENGINE-V1-P06-T001 — Implement filter primitives
- select_by_status (uses indexes.by_status if present; fallback linear)
- filter_by_owner
- filter_by_window (intersects on date_start/date_end)
- apply_limit

### CAM-SNAPSHOT-ENGINE-V1-P06-T002 — Implement query_frontend_v2 (contract parity)
- Build payload with:
  - meta, filters, summary, entities, tasks
- tasks[].status from sheet.status
- tasks[].history from sheet.history
- milestones included fully (if task included)

### CAM-SNAPSHOT-ENGINE-V1-P06-T003 — Implement query_reminders
- Select tasks for window/statuses
- Group by owner_id
- Optional limit_per_owner

### CAM-SNAPSHOT-ENGINE-V1-P06-T004 — Unit tests for query parity
- statuses filter matches old behavior
- window intersects matches old behavior
- history field preserved

---

## PHASE P07 — Wire into entrypoints (API + Notifier)

### CAM-SNAPSHOT-ENGINE-V1-P07-T001 — Bootstrap SnapshotEngine
- В bootstrap собрать:
  - stores (raw/prep/extra)
  - query_engine
  - SnapshotEngine facade

### CAM-SNAPSHOT-ENGINE-V1-P07-T002 — Add new mode/job: snapshot_update
- Добавить режим/endpoint для запуска UpdateJob (timer trigger).

### CAM-SNAPSHOT-ENGINE-V1-P07-T003 — Switch API v2 to SnapshotEngine
- `/api/v2/frontend`:
  - parse query params → FrontendV2Query
  - call engine.frontend_v2(q)
  - return payload
- Запрет: не читать Sheets в API path.

### CAM-SNAPSHOT-ENGINE-V1-P07-T004 — Switch notifier to SnapshotEngine
- Reminder mode uses engine.reminders(q)
- Запрет: не читать Sheets в notifier path.

---

## PHASE P08 — Evidence + docs

### CAM-SNAPSHOT-ENGINE-V1-P08-T001 — Update docs
- `docs/snapshot_engine/architecture.md` final
- `docs/snapshot_engine/migration_plan.md` final
- `docs/system/dataflow.md` add reference: consumers now read PrepCache

### CAM-SNAPSHOT-ENGINE-V1-P08-T002 — Evidence
- Add `docs/evidence/CAM-SNAPSHOT-ENGINE-V1.md`:
  - 1 update run changed=False
  - 1 update run changed=True
  - API v2 example response snippet (no contract changes)
  - notifier selection example

---
```

```md
# priorities_snapshot_engine.md — Приоритеты внедрения Snapshot Engine

## Priority 0 — Контур хранения и обновления
1) P01–P05 (schema + stores + normalizer + prep_builder + update_job)
Причина: пока нет стабильного PrepCache, невозможно безопасно переключать API/notify.

## Priority 1 — QueryEngine parity
2) P06
Причина: единая логика выборок и сохранение контракта v2.

## Priority 2 — Switch consumers
3) P07
Причина: именно это даст выигрыш по скорости и уберет “лес” в runtime.

## Priority 3 — Cleanup/legacy removal (отдельная кампания)
4) После стабилизации можно планировать:
- CAM-LEGACY-PLANNER-RETIRE-V1
- CAM-YDB-SCHEMA-SIMPLIFY-V1 (если решишь убрать старые таблицы)
```
