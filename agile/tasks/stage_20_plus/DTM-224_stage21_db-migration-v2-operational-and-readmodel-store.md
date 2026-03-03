# DTM-224: Stage 21 DB migration v2 (operational + readmodel store)

## Context
- Current YDB adapter stores one payload blob and does not provide normalized operational schema.
- External arbitration requires:
  - operational tables (`dtm_tasks`, `dtm_task_milestones`, `dtm_sync_state`),
  - readmodel table (`dtm_readmodel_frontend_v2`),
  - API v2 read by readmodel snapshot in YDB.

## Goal
- Introduce normalized YDB repos and schema management.
- Introduce source-range hash gate service for YDB sync state.
- Introduce readmodel snapshot repo/service and switch API v2 YDB mode to readmodel fetch.

## Non-goals
- No breaking changes for v1 API.
- No immediate production cutover to `ydb_only` in this task.

## Plan
1. Add YDB schema + repo modules for operational/readmodel stores.
2. Add sync/readmodel services for staged migration.
3. Wire API v2 YDB mode to readmodel snapshot fetch.
4. Update docs (`docs/db/*`, README links).
5. Run local compile/smoke checks.

## Checklist (DoD)
- [x] `src/adapters/ydb/schema.py` added with 4-table `ensure_tables`.
- [x] `src/adapters/ydb/operational_repo.py` added.
- [x] `src/adapters/ydb/readmodel_repo.py` added.
- [x] `src/services/sync_service.py` added (source-range hash gate + operational upserts).
- [x] `src/services/readmodel_builder.py` added (operational -> readmodel snapshot).
- [x] API v2 YDB mode reads `frontend_v2:default` from readmodel table.
- [x] DB docs added (`docs/db/schema.md`, `docs/db/migration-plan.md`).
- [x] Legacy blob write path disabled by default (`LEGACY_BLOB_WRITE=0`) and explicitly logged.
- [x] Hot-path DDL removed from runtime path (`ensure_schema` only with `YDB_MIGRATE_ON_START` / `db_migrate` mode).
- [x] Backoff+jitter added for YDB `RESOURCE_EXHAUSTED`.
- [x] Readmodel builder uses milestones table bulk-load (no N+1 per task reads).
- [x] Operational payload preserves `brand/format_/customer/raw_timing`.
- [x] Unit tests added for source-hash gate / readmodel enums / milestones source / backoff.
- [x] Cloud smoke for readmodel snapshot path (sync -> build -> API v2 over test domain).

## Work log
- 2026-03-02: Created execution task from external migration arbitration prompt.
- 2026-03-02: Added YDB schema module + operational/readmodel repositories with bounded retries and query stats.
- 2026-03-02: Added migration services for YDB sync-state hash gate and readmodel snapshot build.
- 2026-03-02: Switched API v2 YDB source mode to read `dtm_readmodel_frontend_v2` snapshot row.
- 2026-03-02: Added DB docs and README links.
- 2026-03-02: Local smoke passed:
  - `python -m compileall src/adapters/ydb src/services/sync_service.py src/services/readmodel_builder.py index.py`
  - `run_timer.cmd` with `RENDER_SOURCE=ydb`
  - direct YDB smoke (`operational upsert + readmodel build + readmodel fetch`) returned `readmodel_exists=True`.
- 2026-03-02: Wired main runtime to execute YDB migration pipeline (`source-range hash gate -> operational sync -> readmodel build`) in parallel-safe mode under `STORE_MODE in {dual_write,ydb_primary,ydb_only}`.
- 2026-03-02: Removed N+1 milestone replacement by adding bulk replacement path in `OperationalTaskRepo` and switched sync service to one bulk milestone operation.
- 2026-03-02: Fixed Windows console encoding crash in migration logs with safe-print.
- 2026-03-02: Verified API v2 consumes readmodel snapshot from YDB (`readmodelSource=ydb`, `readmodelId=frontend_v2:default`).
- 2026-03-02: Observed transient YDB `RESOURCE_EXHAUSTED` in timer-integrated run; separate retry smoke for readmodel build succeeded and refreshed snapshot (`tasks=14`).
- 2026-03-02: Applied audit hardening:
  - added runtime knobs (`LEGACY_BLOB_WRITE`, `YDB_MIGRATE_ON_START`, exhausted-backoff tuning),
  - removed automatic ensure-schema from hot timer path,
  - switched readmodel build timing source to `dtm_task_milestones`,
  - added missing business fields to normalized operational payload.
- 2026-03-02: Added tests:
  - `tests/services/test_sync_source_hash_gate.py`
  - `tests/services/test_readmodel_enums.py`
  - `tests/services/test_readmodel_uses_milestones_table.py`
  - `tests/services/test_ydb_backoff.py`
- 2026-03-02: Local evidence:
  - `.venv\Scripts\python.exe -m unittest tests.services.test_sync_source_hash_gate tests.services.test_readmodel_enums tests.services.test_readmodel_uses_milestones_table tests.services.test_ydb_backoff tests.api.test_frontend_api_v2_payload tests.services.test_hash_basis -v` -> OK
  - `cmd /c run_timer.cmd` -> migration sync/readmodel path OK, no deferred status.
- 2026-03-02: Unified consumer read path for runtime blocks:
  - `render/notify` source switch now uses normalized repo adapter (`src/adapters/ydb/task_repository.py`) over `dtm_tasks + dtm_task_milestones` (legacy `dtm_operational_tasks` path removed from runtime switch).
  - `v1` API `READMODEL_SOURCE=ydb` path now also uses normalized task repo.
  - Added adapter tests: `tests/adapters/test_ydb_operational_task_repository.py`.
- 2026-03-02: Added compatibility fallback for pre-migration `dtm_tasks` schema (missing `brand/format_/customer/raw_timing`) in `OperationalTaskRepo` read/write paths; timer smoke recovered.
- 2026-03-02: Cloud probe to test contour returned outdated response shape (`readmodelSource` missing), indicating test deployment lag.
- 2026-03-02: Task moved to blocked pending owner manual test deploy; Telegram blocker notification sent (`agent/notify_owner.py --mode blocked ...`).
- 2026-03-03: Manual test deploy confirmed by live probes (`/api/v1/frontend`, `/api/v2/frontend`, `/api/v2/frontend/doc` all `200`), but `meta.readmodelSource/readmodelId` are still absent in v2 payload, so cloud evidence still indicates non-YDB-readmodel source on test contour.
- 2026-03-03: Owner notifications sent via `agent/notify_owner.py`: informational completion note for API cloud verification and blocker note for remaining YDB-readmodel source switch decision.
- 2026-03-03: Repeat deploy verification passed for v2 YDB-readmodel markers (`meta.readmodelSource=ydb`, `readmodelId=frontend_v2:default`), unblocking cloud source-switch concern.
- 2026-03-03: Found v1 regression under YDB source (`1970-01-01` timing dates) caused by YDB Date int parsing in adapter; fixed in `src/adapters/ydb/task_repository.py` with day-offset conversion and covered by new unit test.
- 2026-03-03: Post-fix cloud verification passed:
  - `GET /api/v1/frontend` returns valid task dates (`2026-*`), no fallback `1970-01-01` contamination.
  - `GET /api/v2/frontend` keeps YDB readmodel markers (`meta.readmodelSource=ydb`, `readmodelId=frontend_v2:default`).
  - DB migration cloud smoke blocker is closed.

## Links
- `src/adapters/ydb/schema.py`
- `src/adapters/ydb/operational_repo.py`
- `src/adapters/ydb/readmodel_repo.py`
- `src/services/sync_service.py`
- `src/services/readmodel_builder.py`
- `index.py`
- `docs/db/schema.md`
- `docs/db/migration-plan.md`
- `docs/evidence_db_migration_v2.md`
