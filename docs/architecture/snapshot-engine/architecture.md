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
- Timer/runtime: `src/services/timer_pipeline.py` -> `SnapshotEngine.update(...)`
- HTTP API v2: `src/contexts/access_api/internal/frontend_v2_handler.py` -> `SnapshotEngine.frontend_v2(...)`
- Group query: `src/contexts/telegram_interaction/internal/job_runner.py` -> group-query selection over the snapshot read-model

## Storage Layout
- raw: `snapshot_engine.prefix_raw`
- prep: `snapshot_engine.prefix_prep`
- extra: `snapshot_engine.prefix_extra/default.json`

## Error Boundary
- S3/transport errors -> runtime `TransientError`
- malformed snapshot payload -> runtime `PermanentError`
- HTTP handler maps failures to `503 frontend_source_unavailable`.


