# DB Migration V2 Evidence Checklist

## Scope
- Migration target: normalized YDB operational tables + frontend v2 readmodel snapshot.
- Runtime contour: `STORE_MODE in {dual_write,ydb_primary,ydb_only}`, `READMODEL_SOURCE=ydb`.

## Checklist
- [ ] `db_migrate` executed once (`RUN_MODE=db_migrate`) for target contour.
- [ ] Sync hash gate uses source-range values (`A1:Z2000`) and logs `source_hash`.
- [ ] Operational sync writes `dtm_tasks` + `dtm_task_milestones` + `dtm_sync_state`.
- [ ] Readmodel builder writes `dtm_readmodel_frontend_v2` row `frontend_v2:default`.
- [ ] API v2 returns payload from readmodel snapshot (`meta.readmodelSource=ydb`).
- [ ] Legacy blob write path is disabled by default (`LEGACY_BLOB_WRITE=0`).
- [ ] No `ensure_tables` calls in hot path for prod (`YDB_MIGRATE_ON_START=0`).
- [ ] No `RESOURCE_EXHAUSTED` during smoke run (or retried with bounded backoff and recovered).

## Smoke Log Template
- `source_hash=<...>`
- `sync_changed=true|false`
- `migration_operational_sync ... ydb_queries_count=<n> error_code=<...>`
- `migration_readmodel_build ... changed=true|false tasks_count=<n>`
- `api_ok=true|false`

