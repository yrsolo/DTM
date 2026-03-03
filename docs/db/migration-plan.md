# DTM DB Migration Plan (YDB)

## Rollout Modes
- `STORE_MODE=legacy|dual_write|ydb_primary|ydb_only`
- `READMODEL_SOURCE=legacy|ydb`
- `NOTIFY_SOURCE=legacy|ydb`
- `RENDER_SOURCE=legacy|ydb`
- `LEGACY_BLOB_WRITE=0|1` (default `0`)
- `YDB_MIGRATE_ON_START=0|1` (default `0`, keep off in prod hot path)
- `FORCE_REFRESH=0|1` (default `0`)
- `READMODEL_TTL_MINUTES` (default `9`)
- `PREFLIGHT_TOP_ROWS` (default `50`)
- `FULL_SYNC_INTERVAL_HOURS` (default `24`)

## Stage Order

### Stage 1: Dual-write baseline
- Run one-time schema init via `RUN_MODE=db_migrate`.
- Enable `STORE_MODE=dual_write`.
- Keep read paths on legacy.
- Verify:
  - task upserts land in `dtm_tasks`
  - milestones land in `dtm_task_milestones`
  - `dtm_sync_state` updated by `preflight_hash_50` and `source_hash_full`.
  - `dtm_task_versions` captures active/archive versions.

### Stage 2: Readmodel materialization
- Run readmodel builder job into `dtm_readmodel_frontend_v2`.
- Verify row `frontend_v2:default` exists and updates on source hash changes.
- TTL gate: if readmodel age < `READMODEL_TTL_MINUTES`, skip sync/build in hot path.

### Stage 3: API v2 read from readmodel
- Set `READMODEL_SOURCE=ydb`.
- Verify API v2 does one readmodel query and returns stored `payload_json`.
- Current implementation note:
  - API v2 YDB mode returns stored snapshot as-is (no per-request rebuild/filtering).

### Stage 4: Render/Notify source switch
- Move render and notify to YDB-backed operational/readmodel sources.
- Verify regular timer/morning flows and smoke metrics.

### Stage 5: Primary and strict mode
- Switch `STORE_MODE=ydb_primary` then `STORE_MODE=ydb_only`.
- In production `ydb_only` has no JSON fallback.

## Safety Notes
- Use bounded retries and backoff for `RESOURCE_EXHAUSTED`.
- Keep schema creation idempotent (`ensure_tables`) but execute it only in explicit migrate mode (or controlled non-prod runs).
- Keep cloud verification evidence in sprint/task logs before promotion to prod.
- Use operational runbook for migrate/refresh/rollback steps: `docs/ops/stage22_db_migrate_force_refresh_rollback_runbook.md`.
- Runtime note:
  - Timer flow triggers migration pipeline (`sync_state` + operational + readmodel), and transient YDB exhaustion is logged without stopping legacy render path.
  - forced refresh (`FORCE_REFRESH=1` or runtime flag) rebuilds data/readmodel without version increments for existing tasks.
