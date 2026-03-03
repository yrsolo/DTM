# Entrypoints behavior (Current): `index.py` and `main.py`

This document describes **what actually happens today** when the two entrypoints run.
It is meant to prevent “tribal knowledge” from living only in chat memory.

## `main.py` — job runner (async main)

### Run modes
`mode` is resolved via `resolve_run_mode(mode=..., event=..., triggers=TRIGGERS)`.
Observed modes used in code:
- `db_migrate`
- `timer`
- `test`
- `morning`
- `reminders-only`
- `sync-only`

### db_migrate
If `mode == "db_migrate"`:
1) create `YdbClient(endpoint=YDB_ENDPOINT, database=YDB_DATABASE)`
2) call `ensure_tables(client)`
3) return summary with YDB stats

### Planner bootstrap
For non-migrate modes:
1) build dependencies via `build_planner_dependencies(KEY_JSON, SHEET_INFO, dry_run, mock_external)`
2) create `GoogleSheetPlanner(...)`
3) apply source switches: `_apply_task_source_switches(planner, mode)` based on `NOTIFY_SOURCE`, `RENDER_SOURCE` and `source_policy`

### Optional readmodel freshness marker
If `mode in {timer,test,morning,reminders-only,sync-only}` and `(RENDER_SOURCE=="ydb" or NOTIFY_SOURCE=="ydb")`:
- tries to read readmodel `frontend_v2:default` from YDB and prints a `readmodel_freshness=` marker.

### Legacy file-based hash gate (optional)
If `MIGRATION_ENABLE_SOURCE_HASH_GATE` and `mode in {timer,test,sync-only}`:
- builds a hash basis from tasks loaded from the **Sheets repository** (not from snapshot ranges)
- evaluates `evaluate_hash_gate(...)` using state file `MIGRATION_HASH_GATE_STATE_FILE`
- sets `allow_sync` accordingly

> Note: This is separate from the YDB-based source snapshot hash gate.

### Core use-case execution
Calls `run_planner_use_case(planner, mode, allow_sync=allow_sync)` which drives reminders/render etc.
Then reads `tasks = source_task_repository.get_all_tasks()`.

### Legacy blob write (disabled by default)
If `LEGACY_BLOB_WRITE` and `STORE_MODE in {dual_write,ydb_primary,ydb_only}` and mode in {timer,test,sync-only}:
- writes legacy `dtm_operational_tasks` via `build_operational_store(...).upsert_tasks(records)`.
Else prints: `migration_store_write=skipped write_path=normalized_only`.

### YDB normalized pipeline (sync + readmodel)
This block runs if:
- `STORE_MODE in {dual_write,ydb_primary,ydb_only}`
- `mode in {timer,test,sync-only}`
- `allow_sync == True`

Steps:
1) build `source_id` string based on sheet name and range `A1:Z2000`
2) create `OperationalTaskRepo(endpoint, database, ensure_schema=YDB_MIGRATE_ON_START)`
3) create `YdbSyncService(operational_repo, write_legacy_milestones=WRITE_LEGACY_MILESTONES)`
4) read snapshots from Sheets repository:
   - preflight range: `A1:Z{PREFLIGHT_TOP_ROWS}`
   - full range: `A1:Z2000`
   Each snapshot includes `values + colors`.
5) transform planner tasks to operational payload: `_task_to_operational_payload(task)`
6) read existing readmodel row `frontend_v2:default` and apply TTL skip:
   - `ttl_skip = age_seconds < READMODEL_TTL_MINUTES * 60` (unless `force_refresh`)
7) if ttl_skip: skip sync (`migration_operational_sync=skipped reason=readmodel_ttl_fresh`)
8) else run sync:
   - `sync_service.run(source_id, preflight_snapshot, full_snapshot, normalized_tasks, force_refresh, FULL_SYNC_INTERVAL_HOURS)`
   - prints marker `migration_operational_sync=...`
9) if sync succeeded and not ttl_skip:
   - build readmodel via `FrontendReadmodelBuilderService(...).run(readmodel_id="frontend_v2:default")`
   - prints marker `migration_readmodel_build=...`
10) always prints `migration_defer_status sync_deferred=... readmodel_deferred=...`

### Error handling
- sync exceptions set `sync_deferred=True` and attempt to write last_error into `dtm_sync_state`.
- readmodel exceptions set `readmodel_deferred=True`.

### Key switches influencing behavior
- `STORE_MODE`: {json_only, dual_write, ydb_primary, ydb_only}
- `LEGACY_BLOB_WRITE`: enables legacy `dtm_operational_tasks` writes
- `MIGRATION_ENABLE_SOURCE_HASH_GATE`: enables separate file-based hash gate
- `PREFLIGHT_TOP_ROWS`: rows used for preflight snapshot hash
- `FULL_SYNC_INTERVAL_HOURS`: force full sync at least every N hours
- `READMODEL_TTL_MINUTES`: TTL to skip sync if readmodel is fresh
- `FORCE_REFRESH`: bypass TTL and hash gates, but must not bump versions
- `WRITE_LEGACY_MILESTONES`: whether to maintain legacy milestones table (compat)

## `index.py` — HTTP entrypoint

### What it currently does
`index.py` is a large multi-purpose handler:
- parse raw serverless event → method/path/query/body
- route to API v1 and v2 endpoints
- supports “group query” flows (Telegram chat commands)
- may call into planner logic and/or YDB readmodel repositories

### Intended direction (not implemented in this document)
- `index.py` should become thin: parse + route → call `src/handlers/api.py`.
- group-query should live in `src/handlers/group_query.py` (or similar).

## Why this doc exists
`index.py` and `main.py` are known hotspots; this doc captures current behavior so refactors can be validated against reality.
