# Snapshot Engine Migration Plan (Archive)

This file preserves the historical hard-cutover migration notes for the snapshot-engine rollout.
It is no longer part of the current runtime documentation set.

Historical policy at the time:
- cutover mode: hard cutover
- runtime source of truth: S3 prep snapshot
- YDB readmodel was removed from the API v2 runtime path

Historical rollout steps:
1. Enable `runtime.snapshot_engine.enabled=true` in `config/runtime.yaml`.
2. Configure `bucket/prefix_raw/prefix_prep/prefix_extra`.
3. Deploy runtime with snapshot engine handlers/pipeline.
4. Run timer/sync mode to build fresh snapshots.
5. Verify:
   - `/api/v2/frontend` returns live payload
   - `meta.readmodelSource = "s3_snapshot"`
   - filters/limit/window work as expected

Historical rollback note:
- hard cutover required explicit owner decision and separate change set

Current readers should use:
- `docs/system/architecture.md`
- `docs/system/runbook.md`
- `docs/snapshot_engine/README.md`
