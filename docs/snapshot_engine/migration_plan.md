# Migration Plan (Hard Cutover)

## Policy
- cutover mode: hard cutover
- runtime source of truth: S3 prep snapshot
- YDB readmodel is not used by API v2 runtime path

## Rollout Steps
1. Enable `runtime.snapshot_engine.enabled=true` in `config/runtime.yaml`.
2. Configure `bucket/prefix_raw/prefix_prep/prefix_extra`.
3. Deploy runtime with snapshot engine handlers/pipeline.
4. Run timer/sync mode to build fresh snapshots.
5. Verify:
   - `/api/v2/frontend` returns live payload
   - `meta.readmodelSource = "s3_snapshot"`
   - filters/limit/window work as expected

## Rollback
This campaign uses hard cutover; rollback requires explicit owner decision and separate change-set.
