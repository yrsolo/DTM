# CAM-SNAPSHOT-PREP-BULK-REFORM-V1

## Goal

Remove N+1 S3 reads from `build_prep`, switch snapshot extras to one bulk canonical object, and add detailed prep-build timings without changing public API contracts.

## Scope

- bulk extra snapshot storage under `snapshots/{env}/extra/default.json`
- hard runtime switch from per-task extra layout to bulk extra snapshot
- one-time migration script from per-task objects to bulk snapshot
- detailed prep-build sub-metrics:
  - `extra_load_ms`
  - `orphan_reconcile_ms`
  - `task_view_build_ms`
  - `prep_index_build_ms`
- attachment metadata mutation path updated to bulk extra snapshot
- docs, tracking, and rollout evidence

## Non-goals

- no public API contract changes
- no render algorithm refactor
- no snapshot source/normalizer redesign
- no prod rollout in the same change set

## Implementation skeleton reference

- Primary source: owner-approved execution plan in chat
- Trust level: high for active snapshot-engine path and current bottleneck hypothesis after code verification
- Existing baseline:
  - `src/snapshot_engine/prep_builder.py`
  - `src/snapshot_engine/stores/s3_store.py`
  - `src/snapshot_engine/update_job.py`
  - `src/snapshot_engine/engine.py`
  - `tests/snapshot_engine/test_prep_builder.py`
  - `tests/snapshot_engine/test_update_job_timings.py`

## DoD

- active runtime reads extras from one bulk extra snapshot
- `build_prep` no longer performs per-task S3 reads
- snapshot update emits prep sub-metrics
- one-time migration script exists and preserves attachment metadata
- attachment upload flow still works
- `/api/v2/frontend`, `/info`, notify, and render remain contract-compatible
