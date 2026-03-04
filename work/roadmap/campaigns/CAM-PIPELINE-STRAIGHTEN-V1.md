# CAM-PIPELINE-STRAIGHTEN-V1 — Выпрямить пайплайн (1 sync, 1 gate, preflight действительно экономит)

## Goal
Сделать runtime путь данных **прямым и однозначным**:
- один канонический SyncService
- один канонический hash gate (по snapshot values+colors в YDB sync_state)
- preflight действительно экономит чтение full snapshot
- никаких “вторых гейтов” в main.py

## Problem statement
Сейчас пайплайн блуждает из-за:
1) двух sync реализаций (`src/services/sync_service.py` и `src/services/sync/sync_service.py`);
2) двух гейтов (“старый” в main.py через MIGRATION_ENABLE_SOURCE_HASH_GATE и “новый” в YdbSyncService);
3) preflight читается, но full snapshot читается всё равно всегда.

Это усложняет код, повышает вероятность расхождений поведения, и увеличивает лишние вызовы (Sheets/YDB).

## Scope
- Консолидация sync: оставить один код-путь.
- Удалить/обезвредить старый hash gate в main.py.
- Изменить pipeline runtime так, чтобы full snapshot читался только когда нужно.

## Non-goals
- Не заниматься тонким refactor entrypoints (это отдельная кампания).
- Не менять бизнес-логику нормализации/версий/милстоунов.
- Не менять API контракт.

## Deliverables
- Единственный SyncService, используемый runtime.
- Удалённый/отключённый MIGRATION_ENABLE_SOURCE_HASH_GATE путь.
- Оптимизированный read_source_snapshot: full fetch только при необходимости.
- Обновлённый `docs/system/dataflow.md` (короткая правка: один gate).

## Phases & tasks

### P01 — Single SyncService
- T001: Найти реальный runtime import/usage обоих sync_service модулей.
- T002: Выбрать канонический (скорее `src/services/sync_service.py` как “верхний”).
- T003: Второй модуль:
  - либо удалить,
  - либо переместить в `src/services/legacy_sync/` + добавить big DEPRECATED header
  - + запретить использование (grep check / comment in AGENTS.md)
- T004: Прогнать unit/smoke тесты.

### P02 — Single hash gate (remove old main gate)
- T001: В main.py найти всё, что связано с:
  - MIGRATION_ENABLE_SOURCE_HASH_GATE
  - build_hash_basis / evaluate_hash_gate / save_last_hash / state file
- T002: Удалить эту логику из runtime path timer/job.
  - Решение “allow_sync” должно приниматься только внутри `YdbSyncService.run()` по dtm_sync_state.
- T003: Если нужно оставить для отладки — спрятать под явный dev-only флаг и вынести в отдельный script, не в main pipeline.

### P03 — Make preflight actually cheap
- T001: В `src/services/pipeline_runtime.py::run_ydb_sync_readmodel_pipeline` (или где это сейчас живёт):
  - изменить порядок:
    1) fetch preflight snapshot (A1:Z50)
    2) call sync_service.preflight_decision(preflight_hash) или run() с параметром “preflight only”
    3) если preflight says “no sync needed” и daily full not stale — НЕ читать full snapshot
    4) читать full snapshot только если needed
- T002: В YdbSyncService (если необходимо) разделить:
  - `decide(preflight_hash, now) -> NeedFullSync(bool, reason)`
  - `run_full(full_snapshot, ...)`
  (либо оставить run(), но дать возможность не требовать full_snapshot в no-op case)
- T003: Логирование:
  - `full_snapshot_fetch=skipped reason=preflight_unchanged`
  - это важно для evidence.

### P04 — Evidence & docs
- T001: Обновить `docs/system/dataflow.md`: один gate, preflight экономит full fetch.
- T002: Обновить smoke/лог evidence:
  - показать run без изменений → full snapshot fetch skipped
  - run с изменениями → full snapshot fetch performed

## DoD
- В runtime существует ровно один SyncService.
- В main.py нет второго gate, который решает allow_sync.
- При отсутствии изменений full snapshot не читается.
- Док `dataflow.md` соответствует коду.
