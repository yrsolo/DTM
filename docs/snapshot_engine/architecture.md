# Snapshot Engine Architecture

## Components
- `src/snapshot_engine/update_job.py`
  - `TaskSourceSheetsAdapter`
  - `SheetSnapshotHasher`
  - `SheetsTaskNormalizer`
  - `UpdateJob`
- `src/snapshot_engine/prep_builder.py`
  - merge `RawSnapshot` + `TaskExtra`
  - build indexes (`by_status`, `by_owner`)
- `src/snapshot_engine/query_engine.py`
  - API v2 query/filter path over `PrepSnapshot`
- `src/snapshot_engine/stores/s3_store.py`
  - `S3RawCache`
  - `S3PrepCache`
  - `S3ExtraStore`

## Runtime Usage
- Timer/runtime: `src/services/timer_pipeline.py` -> `SnapshotEngine.update(...)`
- HTTP API v2: `src/entrypoints/http/frontend_v2_handler.py` -> `SnapshotEngine.frontend_v2(...)`
- Group query: `src/entrypoints/http/group_query_handler.py` -> API payload from snapshot engine

## Storage Layout
- raw: `snapshot_engine.prefix_raw`
- prep: `snapshot_engine.prefix_prep`
- extra: `snapshot_engine.prefix_extra/{task_id}.json`

## Error Boundary
- S3/transport errors -> runtime `TransientError`
- malformed snapshot payload -> runtime `PermanentError`
- HTTP handler maps failures to `503 frontend_source_unavailable`.
