# Snapshot Engine Architecture

## Components
- `src/contexts/snapshot/application/update_job.py`
  - `TaskSourceSheetsAdapter`
  - `SheetSnapshotHasher`
  - `SheetsTaskNormalizer`
  - `UpdateSnapshotJob`
- `src/contexts/snapshot/internal/engine/prep_builder.py`
  - merge `RawSnapshot` + `TaskExtra`
  - build indexes (`by_status`, `by_owner`)
- `src/contexts/snapshot/internal/engine/query_engine.py`
  - API v2 query/filter path over `PrepSnapshot`
- `src/contexts/snapshot/internal/engine/stores/s3_store.py`
  - `S3RawCache`
  - `S3PrepCache`
  - `S3ExtraStore`

## Runtime Usage
- Timer/runtime: `src/platform/runtime/timer_pipeline.py` -> `src/contexts/snapshot/module.py:get_update_api(...)` -> `SnapshotUpdateApi.update(...)`
- Primary browser read: `src/contexts/access_api/application/browser_read_api.py` -> `src/contexts/access_api/internal/primary_task_list_read_api.py` -> `src/contexts/access_api/application/primary_task_list_read_service.py` -> `SnapshotQueryApi.frontend_v2(...)`
- Group query: `src/contexts/telegram_interaction/internal/job_runner.py` -> group-query selection over the snapshot read-model

## Storage Layout
- raw: `snapshot_engine.prefix_raw`
- prep: `snapshot_engine.prefix_prep`
- extra: `snapshot_engine.prefix_extra/default.json`

## Error Boundary
- S3/transport errors -> runtime `TransientError`
- malformed snapshot payload -> runtime `PermanentError`
- browser-read adapter maps snapshot-read failures to `503 frontend_source_unavailable`.


