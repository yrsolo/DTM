# DB Migration V2 Finalization Plan (DTM-227)

## Stage 0 Audit (current code entrypoints)

### Sync job (hash gate + operational sync)
- Runtime entry: `main.py:main()`
- Current YDB sync call:
  - `YdbSyncService.run(...)` from `src/services/sync_service.py`
  - source values read by `_read_source_range_values(...)`
- Current defer behavior:
  - `sync_deferred` and `readmodel_deferred` flags in `main.py`

### Readmodel builder
- Runtime call site: `main.py:main()`
- Builder implementation:
  - `FrontendReadmodelBuilderService.run(...)` in `src/services/readmodel_builder.py`
- Repo target table:
  - `FrontendReadmodelRepo` (`dtm_readmodel_frontend_v2`)

### API v2 readmodel source
- HTTP handler entry: `index.py:handler(...)`
- API v2 path:
  - `_handle_frontend_api_v2_if_requested(...)`
- YDB readmodel branch:
  - reads `FrontendReadmodelRepo.get_readmodel("frontend_v2:default")`
  - returns stored `payload_json`

### Legacy blob-store contour
- Legacy operational adapter: `src/adapters/store_ydb.py` (table `dtm_operational_tasks`)
- Legacy write in hot path:
  - `main.py` block under `LEGACY_BLOB_WRITE`
- Current state:
  - guarded by `LEGACY_BLOB_WRITE` (default off)

## Gaps vs finalization prompt
- Missing `dtm_task_versions` table and archive lifecycle logic.
- Missing preflight top-50 hash state (`preflight_hash_50`) and daily full-sync gate.
- Missing explicit forced-refresh mode that rebuilds data/readmodel without version bump.
- Missing evidence/checklist updates for new finalization flow.
