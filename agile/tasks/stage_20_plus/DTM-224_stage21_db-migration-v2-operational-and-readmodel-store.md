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
- [ ] Cloud smoke for readmodel snapshot path.

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

## Links
- `src/adapters/ydb/schema.py`
- `src/adapters/ydb/operational_repo.py`
- `src/adapters/ydb/readmodel_repo.py`
- `src/services/sync_service.py`
- `src/services/readmodel_builder.py`
- `index.py`
- `docs/db/schema.md`
- `docs/db/migration-plan.md`
