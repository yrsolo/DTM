# DB Migration V2 Evidence Checklist

## Scope
- Migration target: normalized YDB operational tables + frontend v2 readmodel snapshot.
- Runtime contour: `STORE_MODE in {dual_write,ydb_primary,ydb_only}`, `READMODEL_SOURCE=ydb`.

## Smoke command
- `.venv\Scripts\python.exe agent\cloud_smoke_db_migration_v2.py --base-url https://functions.yandexcloud.net/<function_id>`

## Checklist
- [ ] `db_migrate` executed once (`RUN_MODE=db_migrate`) for target contour.
- [ ] Preflight gate uses top-50 source rows (`A1:Z50`, values+colors) and logs `preflight_hash_50`.
- [ ] Full sync gate uses full source rows (`A1:Z2000`, values+colors) and logs `source_hash_full`.
- [ ] Daily full sync rule works (`FULL_SYNC_INTERVAL_HOURS=24` by default).
- [ ] Operational sync writes `dtm_tasks` + `dtm_task_milestones` + `dtm_sync_state`.
- [ ] Version archive writes `dtm_task_versions`:
  - content change => new `version`, previous => `archive`
  - color/status-only change => no version bump
- [ ] Readmodel builder writes `dtm_readmodel_frontend_v2` row `frontend_v2:default`.
- [ ] API v2 returns payload from readmodel snapshot (`meta.readmodelSource=ydb`).
- [ ] forced refresh updates data/readmodel without version increments for existing tasks.
- [ ] Legacy blob write path is disabled by default (`LEGACY_BLOB_WRITE=0`).
- [ ] No `ensure_tables` calls in hot path for prod (`YDB_MIGRATE_ON_START=0`).
- [ ] No `RESOURCE_EXHAUSTED` during smoke run (or retried with bounded backoff and recovered).

## Smoke Log Template
- `preflight_hash_50=<...>`
- `source_hash_full=<...>`
- `full_sync_performed=true|false`
- `migration_operational_sync ... ydb_queries_count=<n> error_code=<...>`
- `migration_readmodel_build ... changed=true|false tasks_count=<n>`
- `api_ok=true|false`
