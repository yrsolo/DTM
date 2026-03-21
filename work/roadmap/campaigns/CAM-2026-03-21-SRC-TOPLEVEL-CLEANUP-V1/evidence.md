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
- folded the thin top-level root dispatcher package into the canonical `entrypoints` tree:
  - `src/entrypoint/{handler,modes,parse_request,responses}.py` -> `src/entrypoints/root/*`
  - `index.py` now imports the top router from `src.entrypoints.root.handler`
  - aligned tests moved from `tests/entrypoint/*` -> `tests/entrypoints/root/*`
- moved loose cross-context integration adapters out of the generic `src/adapters` shelf into platform-owned homes:
  - `src/adapters/telegram.py` -> `src/platform/integrations/telegram/notifier.py`
  - `src/adapters/llm_google.py` -> `src/platform/integrations/llm/google.py`
  - `src/adapters/llm_openai.py` -> `src/platform/integrations/llm/openai.py`
  - `src/adapters/llm_yandex.py` -> `src/platform/integrations/llm/yandex.py`
- moved the operational store utility out of `src/adapters` into platform infra:
  - `src/adapters/store_ydb.py` -> `src/platform/infra/operational_store.py`
  - aligned tests moved from `tests/adapters/*store*` -> `tests/platform/infra/*`
- moved the remaining provider packages out of `src/adapters` into role-true homes:
  - `src/adapters/google_sheets/*` -> `src/platform/integrations/google_sheets/*`
  - `src/adapters/ydb/*` -> `src/platform/infra/ydb/*`
  - aligned tests moved from `tests/adapters/*ydb*` -> `tests/platform/infra/ydb/*`
- removed dead placeholder files from the adapter root:
  - `src/adapters/google_sheets_reader.py`
  - `src/adapters/google_sheets_renderer.py`
- removed the old tracked adapter root entirely:
  - `src/adapters/__init__.py`
- moved the aligned active tests with those new owning paths:
  - `tests/platform/runtime/test_timer_pipeline.py`
  - `tests/contexts/snapshot/test_sheets_normalized_source.py`
- removed isolated tests that existed only for those dead service-era leftovers:
  - `tests/services/test_readmodel_uses_milestones_table.py`
  - `tests/services/test_source_policy.py`
  - `tests/services/test_sync_source_hash_gate.py`
- tracked top-level `src/` map now reads through active architecture zones only:
  - `app`, `archive`, `commands`, `config`, `contexts`, `core`, `entrypoints`, `infra`, `observability`, `platform`, `worker`
- `src/__pycache__` may reappear during local test runs; it is treated as Python runtime noise rather than an architecture root and is no longer part of the structural kill criteria.
- `src/entrypoint`, `src/services`, and `tests/entrypoint` may still exist locally as `__pycache__` directories during a dirty worktree test run; they no longer exist as tracked Python roots.
- guardrail strengthened in `tests/architecture/test_guardrails_v0.py` so removed top-level historical roots, `entrypoints_adapters`, `src/entrypoint`, and `tests/entrypoint` must not return as tracked Python roots.
- verification after this cut stayed green:
  - `python -m unittest tests.contexts.access_api.test_masking tests.api.test_frontend_api_routing tests.architecture.test_guardrails_v0 tests.entrypoints.test_import_safety tests.api.test_command_queue_foundation tests.contexts.attachments.test_attach_task_file_job tests.services.test_pipeline_runtime -v`
  - `python -m unittest tests.architecture.test_guardrails_v0 tests.entrypoints.test_import_safety tests.api.test_frontend_api_routing tests.contexts.access_api.test_masking tests.api.test_command_queue_foundation tests.contexts.attachments.test_attach_task_file_job tests.contexts.attachments.test_delete_task_attachment_job tests.contexts.attachments.test_cleanup_task_attachments_job tests.contexts.attachments.test_generate_attachment_preview_job tests.services.test_pipeline_runtime tests.entrypoints.test_planner_runtime_entry -v`
  - `python -m unittest tests.architecture.test_guardrails_v0 tests.architecture.test_target_skeleton_imports tests.entrypoints.root.test_handler tests.entrypoints.root.test_parse_request tests.entrypoints.test_import_safety tests.api.test_frontend_api_routing tests.api.test_command_queue_foundation tests.entrypoints.test_planner_runtime_entry -v`
- verification after the platform-integration cut stayed green:
  - `python -m unittest tests.architecture.test_guardrails_v0 tests.entrypoints.test_import_safety tests.entrypoints.test_planner_runtime_entry tests.contexts.reminders.test_send_reminders_job tests.contexts.telegram_interaction.test_group_query_reply_job tests.api.test_command_queue_foundation tests.api.test_frontend_api_routing -v`
- verification after the adapter-root reduction stayed green:
  - `python -m unittest tests.architecture.test_guardrails_v0 tests.entrypoints.test_import_safety tests.entrypoints.test_planner_runtime_entry tests.contexts.reminders.test_send_reminders_job tests.contexts.telegram_interaction.test_group_query_reply_job tests.api.test_command_queue_foundation tests.api.test_frontend_api_routing tests.platform.infra.test_operational_store tests.platform.infra.test_operational_store_repository -v`
- verification after removing the tracked adapter root stayed green:
  - `python -m unittest tests.architecture.test_guardrails_v0 tests.entrypoints.test_import_safety tests.entrypoints.test_planner_runtime_entry tests.api.test_command_queue_foundation tests.api.test_frontend_api_routing tests.contexts.reminders.test_send_reminders_job tests.contexts.telegram_interaction.test_group_query_reply_job tests.contexts.snapshot.test_sheets_normalized_source tests.core.test_timing_year_modes tests.services.test_ydb_backoff tests.platform.infra.test_operational_store tests.platform.infra.test_operational_store_repository tests.platform.infra.ydb.test_operational_repo_dates tests.platform.infra.ydb.test_operational_repo_history tests.platform.infra.ydb.test_operational_repo_milestones_bulk tests.platform.infra.ydb.test_operational_repo_versions_bulk tests.platform.infra.ydb.test_operational_task_repository tests.platform.infra.ydb.test_schema_history_column -v`
- next blocker is no longer the adapter root; tracked `src/adapters` is gone from the active repo map.
- the loudest remaining architectural split is now the coexistence of `src/app` and `src/platform`: bootstrap/context live in `app`, while runtime/integrations/infra now live in `platform`.
- from here the next step is no longer a safe top-level cleanup. It is a design choice: keep `app` as a justified composition/config contour, or fold it deeper into `platform` for one tighter runtime map.
