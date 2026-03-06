# CAM-SNAPSHOT-ENGINE-V1 Evidence

## Trust Gate
- source: `src/services/timer_pipeline.py`, `src/services/readmodel_builder.py`, `src/entrypoints/http/frontend_v2_handler.py`
- last_verified_at: 2026-03-06
- verified_by: codex
- evidence:
  - current canonical runtime path is YDB sync + YDB readmodel build + readmodel API serving
  - no `src/snapshot_engine` modules exist in active tree
  - API v2 handler currently reads `FrontendReadmodelRepo` and applies query filters over readmodel payload
- trust_level: high
- notes:
  - owner decision fixed: hard cutover to S3 snapshot engine without runtime fallback to YDB readmodel

## Migration Policy
- `status` remains normalized color-derived status.
- `history` remains raw textual status from source.
- runtime source of truth after cutover: S3 prep snapshot only.

## Execution Evidence
- implemented modules:
  - `src/snapshot_engine/*` (model/interfaces/serialization/prep_builder/update_job/query_engine/engine)
  - `src/snapshot_engine/stores/s3_store.py`
  - `src/entrypoints_adapters/api_v2_adapter.py`
  - `src/entrypoints_adapters/notifier_adapter.py`
- runtime integration:
  - `src/services/timer_pipeline.py` switched to `SnapshotEngine.update(...)`
  - `src/entrypoints/http/frontend_v2_handler.py` switched to snapshot query path
  - `src/entrypoints/http/group_query_handler.py` switched to snapshot-backed active-task flow
- config integration:
  - typed `runtime.snapshot_engine` in `src/config/schema.py`
  - loader parsing + fail-fast validation in `src/config/loader.py`
  - defaults in `config/runtime.yaml`

## Test Evidence
- `python -m unittest tests.api.test_frontend_api_routing -v` -> OK
- `python -m unittest tests.api.test_frontend_api_v2_payload -v` -> OK
- `python -m unittest tests.services.test_pipeline_runtime -v` -> OK
- `python -m unittest tests.services.test_planner_pipeline_job -v` -> OK
- `python -m unittest tests.snapshot_engine.test_normalizer -v` -> OK
- `python -m unittest tests.snapshot_engine.test_prep_builder -v` -> OK
- `python -m unittest tests.snapshot_engine.test_query_engine -v` -> OK
- `python -m unittest tests.snapshot_engine.test_s3_store -v` -> OK

## Notes
- `boto3` import moved to lazy runtime initialization inside S3 store to avoid module import failures in environments where S3 runtime path is not executed.
- Post-cutover incident fixes on test contour:
  - fixed deploy bundle include set to ship `config/**/*.yaml` into YC function package.
  - switched snapshot bucket config to `dtm-front`.
  - added function secrets wiring for `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` from lockbox.
  - hardened update job self-heal:
    - corrupted raw cache no longer blocks rebuild,
    - prep cache is rebuilt when missing/corrupted even if raw hash is unchanged.

## Live Smoke (Test contour)
- Date: 2026-03-06
- Command: `scripts\\invoke_cloud_timer.cmd --sync-only --force-refresh --live`
- API check: `GET /api/v2/frontend?statuses=work,pre_done&limit=20&include_people=true`
- Result:
  - HTTP `200`
  - `meta.readmodelSource = "s3_snapshot"`
  - `meta.queryFilterApplied = true`
  - `summary.tasksReturned = 12`

## Bucket migration
- Moved snapshot storage from `dtm-front` to private `dtm` bucket.
- Data copy performed for existing keys:
  - `snapshots/raw/default.json`
  - `snapshots/prep/default.json`
- Added isolated test namespace bootstrap objects:
  - `snapshots/test/raw/default.json`
  - `snapshots/test/prep/default.json`
- Config defaults updated to `snapshot_engine.bucket=dtm` and `object_storage.bucket_default=dtm`.
