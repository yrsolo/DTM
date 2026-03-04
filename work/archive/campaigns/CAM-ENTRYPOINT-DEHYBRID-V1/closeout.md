# CAM-ENTRYPOINT-DEHYBRID-V1 Closeout

## Result
- `index.py` no longer imports or calls `main.main`.
- Runtime entry is shared via `src/entrypoints/runtime/planner_runtime_entry.py`.
- Direct `core.*` imports were removed from `index.py`; remaining legacy bindings are isolated under `src/legacy/*`.
- Entrypoint docs were synced to current runtime shape.

## Verification Summary
- grep checks confirm no `index -> main` coupling and no direct `core.*` imports in `index.py`.
- smoke pack is green (`26` tests):
  - `tests.api.test_frontend_api_routing`
  - `tests.services.test_pipeline_runtime`
  - `tests.services.test_planner_pipeline_job`
  - `tests.services.test_sync_source_hash_gate`

## Follow-up
- Next active campaign: `CAM-ENTRYPOINT-HYGIENE-V1`.
