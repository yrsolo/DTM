# CAM-SNAPSHOT-PREP-BULK-REFORM-V1 Evidence

## Trust gate

- source: active snapshot-engine code and current tests
- last_verified_at: 2026-03-10
- verified_by: Codex
- evidence:
  - `src/snapshot_engine/prep_builder.py`
  - `src/snapshot_engine/stores/s3_store.py`
  - `src/snapshot_engine/update_job.py`
  - `src/snapshot_engine/engine.py`
  - `tests/snapshot_engine/test_prep_builder.py`
  - `tests/snapshot_engine/test_s3_store.py`
  - `tests/snapshot_engine/test_update_job_timings.py`
- trust_level: high
- notes:
  - `build_prep_ms` wraps the full `PrepBuilder.build(raw)` path
  - current `S3ExtraStore.get_many()` performs one `get_object` per task id
  - current orphan handling writes per task key in hot path
  - current attachment mutation path still uses per-task extra reads/writes

## Baseline facts

- current extra layout key pattern: `snapshots/{env}/extra/{task_id}.json`
- current prep flow:
  - load extras via per-task `get_many()`
  - reconcile orphans via per-task `mark_orphaned()`
  - build `tasks_by_id`
  - build `by_status` / `by_owner`
- current public behavior to preserve:
  - attachments exposed through `tasks[].attachments`
  - frontend payload does not expose storage key internals

## Planned hard-switch runtime boundary

- new canonical extra key:
  - `snapshots/{env}/extra/default.json`
- runtime compatibility with old per-task extra layout is intentionally dropped after migration
- old per-task objects may remain physically in storage temporarily for rollback/reference only

## Local implementation evidence

- added bulk extra snapshot model and prep-build result in:
  - `src/snapshot_engine/model.py`
- replaced `ExtraStore` protocol with bulk snapshot contract:
  - `src/snapshot_engine/interfaces.py`
- `PrepBuilder` now:
  - loads one bulk extra snapshot
  - reconciles orphans in memory
  - writes bulk snapshot once only if orphan state changed
  - returns `PrepBuildResult` with:
    - `extra_load_ms`
    - `orphan_reconcile_ms`
    - `task_view_build_ms`
    - `prep_index_build_ms`
  - file: `src/snapshot_engine/prep_builder.py`
- `S3ExtraStore` now reads/writes canonical bulk key:
  - `snapshots/{env}/extra/default.json`
  - file: `src/snapshot_engine/stores/s3_store.py`
- snapshot update path now records prep sub-timings and emits matching metrics:
  - `src/snapshot_engine/update_job.py`
  - `src/jobs/update_snapshot_job.py`
- attachment metadata mutation path now updates bulk extra snapshot:
  - `src/snapshot_engine/engine.py`
- one-time migration script added:
  - `scripts/migrate_extra_store_to_bulk.py`

## Local verification

- focused snapshot-engine regression:
  - `python -m unittest discover -s tests/snapshot_engine -p "test_*.py" -v`
  - result: `21 tests OK`
- attachment/info regression:
  - `python -m unittest tests.jobs.test_attach_task_file_job tests.api.test_info_observability -v`
  - result: `OK`
- compile check:
  - `python -m py_compile src/snapshot_engine/model.py src/snapshot_engine/interfaces.py src/snapshot_engine/serialization.py src/snapshot_engine/prep_builder.py src/snapshot_engine/stores/s3_store.py src/snapshot_engine/update_job.py src/snapshot_engine/engine.py src/jobs/update_snapshot_job.py scripts/migrate_extra_store_to_bulk.py`
  - result: `OK`
- boundary guards:
  - `python scripts/check_no_legacy_entrypoint_imports.py`
  - `python scripts/check_no_legacy_imports.py`
  - result: `OK`

## Pending rollout evidence

- migration still must be run on `test` before deploy-time cutover:
  - `python scripts/migrate_extra_store_to_bulk.py --env test`
- after `test` deploy, capture:
  - before/after `dtm.snapshot.build_prep_ms`
  - new prep sub-metrics
  - attachment metadata still visible through `/api/v2/frontend`

## Test migration evidence

- command:
  - `.venv\Scripts\python.exe scripts/migrate_extra_store_to_bulk.py --env test`
- result:
  - `objects_scanned=0`
  - `valid_extras_migrated=0`
  - `duplicate_task_ids=[]`
  - `invalid_payload_count=0`
  - `bulk_key=snapshots/test/extra/default.json`
- interpretation:
  - `test` contour had no legacy per-task extra objects to migrate
  - hard-switch rollout on `test` is not blocked by existing attachment metadata in old layout

## Live test rollout evidence

- deployed commit on `test`:
  - `92be1bb` `refactor(snapshot): switch prep extras to bulk S3 snapshot and add prep stage timings`
- live endpoints checked:
  - `GET https://dtm-api-test.solofarm.ru/info?format=json`
  - `GET https://dtm-api-test.solofarm.ru/api/v2/frontend?limit=1`
  - `POST https://dtm-api-test.solofarm.ru/admin/commands/update-snapshot`
  - `GET https://dtm-api-test.solofarm.ru/admin/jobs/07ddca664f624d78bad89f9cdc05be24`
- observed live telemetry:
  - `/info?format=json` telemetry block shows current post-hard-switch runtime:
    - `metricsClient=CompositeMetricsClient`
    - `prometheusEnabled=true`
    - `grafanaEnabled=true`
  - `/api/v2/frontend?limit=1` still returns `tasks[].attachments` in the contract
- latest successful `update_snapshot` job timings:
  - `fetch_sheet_ms = 2701.5758450000008`
  - `normalize_ms = 1853.593087000002`
  - `build_prep_ms = 58.85680000000093`
  - `extra_load_ms = 57.29412700000225`
  - `orphan_reconcile_ms = 0.07505100000315679`
  - `task_view_build_ms = 0.8027750000003664`
  - `prep_index_build_ms = 0.3760350000021617`
  - `write_raw_ms = 551.484103`
  - `write_prep_ms = 472.32493399999953`
  - `total_duration_ms = 5761.976256000001`
- before/after conclusion:
  - previous observed `build_prep_ms` on `test` was approximately `12117 ms`
  - post-cutover live `build_prep_ms` is approximately `58.86 ms`
  - the dominant prep cost is no longer N+1 S3 reads; the remaining prep time is almost entirely one bulk `extra_load_ms`
- rollout interpretation:
  - hard-switch runtime works on `test`
  - no public API drift was observed on `/api/v2/frontend`
  - the N+1 extra-store hot path is removed from live runtime behavior
