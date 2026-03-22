# Evidence - CAM-2026-03-22-SNAPSHOT-RUNTIME-HUB-REDUCTION-V1

## Trust gate
- source: current snapshot module/application/internal code, current access-api consumers, current snapshot/timer tests, owner critique
- last_verified_at: 2026-03-22
- verified_by: Codex
- evidence:
  - `agent/owner_inputs/crit.md`
  - `src/contexts/snapshot/module.py`
  - `src/contexts/snapshot/application/capabilities.py`
  - `src/contexts/snapshot/internal/runtime_binding.py`
  - `src/contexts/snapshot/internal/engine/engine.py`
  - `src/contexts/snapshot/application/update_job.py`
  - `src/platform/runtime/timer_pipeline.py`
  - `tests/contexts/snapshot/test_query_engine.py`
  - `tests/contexts/snapshot/test_update_job.py`
  - `tests/contexts/access_api/test_frontend_api_routing.py`
- trust_level: high
- notes:
  - this wave narrows the hidden runtime hub without changing contracts or storage behavior

## Result
- `snapshot` application APIs no longer depend on one broad runtime bundle
- `snapshot/module.py` now composes read/query/attachment/update APIs from smaller role-true builders
- the internal runtime layer is reduced to specific builders for stores, query engine, attachment mutations, and update execution
- `get_snapshot_update_api(ctx)` now resolves through the canonical module surface instead of incorrectly constructing `SnapshotUpdateApi(ctx)` directly

## Verification
- `python -m unittest tests.contexts.snapshot.test_query_engine tests.contexts.snapshot.test_update_job tests.contexts.snapshot.test_engine_attach_metadata tests.contexts.snapshot.test_engine_cleanup_attachments tests.contexts.snapshot.test_people_snapshot tests.platform.runtime.test_timer_pipeline tests.contexts.attachments.test_attach_task_file_job tests.contexts.attachments.test_delete_task_attachment_job tests.contexts.attachments.test_generate_attachment_preview_job tests.contexts.access_api.test_frontend_api_routing tests.architecture.test_guardrails_v0 tests.entrypoints.test_import_safety -v`
- Result: `102 tests`, `OK`
