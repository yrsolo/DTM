# CAM-2026-03-21-SRC-TOPLEVEL-CLEANUP-V1 Evidence

## Trust Gate

- source: current top-level `src/` tree and active import graph
  - last_verified_at: `2026-03-21`
  - verified_by: `Codex`
  - evidence:
    - `Get-ChildItem src -Directory`
    - `Get-ChildItem src/jobs,src/render,src/notify,src/snapshot_engine,src/telegram,src/handlers,src/entrypoints_adapters -Force`
    - `rg -n "^from src\\.(...)" src tests`
  - trust_level: `high`
  - notes: current inspection shows several top-level roots no longer contain live Python code, while `src/entrypoints_adapters` survives only as a stray adapter shelf for logic that belongs inside `access_api`.

## Active Tasks

- [x] remove dead top-level historical roots
- [x] remove stray `entrypoints_adapters` root by moving its live helper into `access_api`
- [x] strengthen guardrails so removed roots must not reappear
- [x] verify active tests/imports remain green

## Iteration Notes

- removed dead top-level roots that survived only as pycache or empty historical directories:
  - `src/jobs`
  - `src/render`
  - `src/notify`
  - `src/snapshot_engine`
  - `src/telegram`
  - `src/handlers`
- removed `src/entrypoints_adapters` after moving `build_frontend_query` into `src/contexts/access_api/internal/frontend_query.py`
- moved browser masking from `src/services/access/masking.py` into `src/contexts/access_api/internal/masking.py`, so `services/access` is no longer an owning-looking shelf in the repo map
- removed dead service-era shelves that were no longer part of the active graph:
  - `src/services/notify`
  - `src/services/render`
  - `src/services/mappers`
  - `src/services/sync`
- removed dead service-era runtime leftovers that were no longer part of the active graph:
  - `src/services/pipeline_runtime.py`
  - `src/services/readmodel_builder.py`
  - `src/services/source_policy.py`
  - `src/services/sync_service.py`
- removed thin service-era protocol shelf that survived only as a delegating type bucket for `TimerJob`:
  - `src/services/usecases/contracts.py`
  - `src/services/usecases/__init__.py`
- moved the last live technical pieces out of `src/services` into role-true homes:
  - `src/platform/errors.py`
  - `src/platform/runtime/timer_pipeline.py`
  - `src/contexts/snapshot/adapters/sources/*`
- removed the old tracked `src/services` Python surface entirely:
  - `src/services/errors.py`
  - `src/services/timer_pipeline.py`
  - `src/services/sources/*`
  - `src/services/__init__.py`
- moved the aligned active tests with those new owning paths:
  - `tests/platform/runtime/test_timer_pipeline.py`
  - `tests/contexts/snapshot/test_sheets_normalized_source.py`
- removed isolated tests that existed only for those dead service-era leftovers:
  - `tests/services/test_readmodel_uses_milestones_table.py`
  - `tests/services/test_source_policy.py`
  - `tests/services/test_sync_source_hash_gate.py`
- top-level `src/` map now reads through active architecture zones only:
  - `adapters`, `app`, `archive`, `commands`, `config`, `contexts`, `core`, `entrypoint`, `entrypoints`, `infra`, `observability`, `platform`, `services`, `worker`
- `src/__pycache__` may reappear during local test runs; it is treated as Python runtime noise rather than an architecture root and is no longer part of the structural kill criteria.
- guardrail strengthened in `tests/architecture/test_guardrails_v0.py` so removed top-level historical roots and `entrypoints_adapters` must not exist as live Python roots.
- verification after this cut stayed green:
  - `python -m unittest tests.contexts.access_api.test_masking tests.api.test_frontend_api_routing tests.architecture.test_guardrails_v0 tests.entrypoints.test_import_safety tests.api.test_command_queue_foundation tests.contexts.attachments.test_attach_task_file_job tests.services.test_pipeline_runtime -v`
  - `python -m unittest tests.architecture.test_guardrails_v0 tests.entrypoints.test_import_safety tests.api.test_frontend_api_routing tests.contexts.access_api.test_masking tests.api.test_command_queue_foundation tests.contexts.attachments.test_attach_task_file_job tests.contexts.attachments.test_delete_task_attachment_job tests.contexts.attachments.test_cleanup_task_attachments_job tests.contexts.attachments.test_generate_attachment_preview_job tests.services.test_pipeline_runtime tests.entrypoints.test_planner_runtime_entry -v`
- next blocker is no longer `src/services` itself. The loudest remaining competing center in the top-level map is the dual-root entry contour:
  - `src/entrypoint`
  - `src/entrypoints`
- resolving that split now requires a deliberate redesign choice, not another safe cleanup pass.
