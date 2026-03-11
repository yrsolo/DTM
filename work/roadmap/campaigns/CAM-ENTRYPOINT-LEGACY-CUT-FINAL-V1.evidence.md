# Evidence - CAM-ENTRYPOINT-LEGACY-CUT-FINAL-V1

## Trust Gate

- source:
  - `index.py`
  - `src/entrypoints/http/router.py`
  - `src/entrypoints/http/frontend_v2_handler.py`
  - `src/entrypoints/runtime/planner_runtime_entry.py`
  - `main.py`
  - `src/entrypoints/jobs/legacy_store_write_job.py`
  - `src/entrypoints/jobs/planner_pipeline_job.py`
  - `src/entrypoints/jobs/planner_setup_job.py`
  - `src/entrypoints/jobs/source_switch_job.py`
- last_verified_at: 2026-03-09
- verified_by: codex
- trust_level: high
- evidence:
  - `index.py` currently acts as bootstrap shell, MQ worker shell, HTTP shell, and trigger/runtime shell simultaneously.
  - `index.py` imports command DTOs, MQ helpers, HTTP parsing helpers, runtime execution helpers, `HttpRouter`, `FrontendReadmodelRepo`, and late-imports `planner_runtime_entry`.
  - `HttpRouter` still accepts `frontend_readmodel_repo_cls`, but `FrontendV2Handler` ignores it and builds payload from Snapshot Engine directly.
  - `planner_runtime_entry.py` still imports legacy store/planner helpers and contains `use_legacy_planner = normalized_mode.startswith("legacy_planner_")`.
  - live product features (API v2, `/info`, render v2, notify v2, telegram intake, group query reply, attachments metadata) do not require legacy planner/store branch as standard runtime behavior.

## Notes

- Legacy code is still valuable as reference; this CAM archives it rather than immediately deleting it.
- The cleanup target is standard runtime only. Broader `core/*` and readmodel debt are follow-up work.

## Implementation Evidence

- implemented:
  - `index.py`
    - reduced to bootstrap + dispatcher shell
    - removed queue/HTTP/runtime/parser/YDB imports
  - `src/entrypoints/index_dispatcher.py`
    - top-level event-kind dispatch
  - `src/entrypoints/event_classifier.py`
    - explicit `QUEUE|HTTP|HEALTHCHECK|TRIGGER|UNKNOWN`
  - `src/entrypoints/http/http_shell.py`
    - owns HTTP request parsing, router dispatch, and explicit runtime fallback
  - `src/entrypoints/queue/worker_shell.py`
    - owns MQ worker invocation path
  - `src/entrypoints/triggers/trigger_shell.py`
    - owns trigger enqueue/direct-runtime fallback
  - `src/entrypoints/runtime/runtime_shell.py`
    - owns bridge from transport shell to standard runtime entry
  - `src/entrypoints/runtime/runtime_contract.py`
    - single source of truth for supported standard modes
  - `src/entrypoints/http/router.py`
    - removed `frontend_readmodel_repo_cls`
  - `src/entrypoints/http/frontend_v2_handler.py`
    - removed unused repo class parameter
  - `src/entrypoints/runtime/planner_runtime_entry.py`
    - removed `use_legacy_planner`
    - removed legacy store write / planner use-case / readmodel probe imports and branch
    - explicit unsupported-mode result for legacy and unknown modes
  - archived reference-only helpers under:
    - `src/legacy/entrypoints/jobs/legacy_store_write_job.py`
    - `src/legacy/entrypoints/jobs/planner_pipeline_job.py`
    - `src/legacy/entrypoints/jobs/planner_setup_job.py`
    - `src/legacy/entrypoints/jobs/source_switch_job.py`
  - guard:
    - `scripts/check_no_legacy_entrypoint_imports.py`

## Verification

- last_verified_at: 2026-03-09
- verified_by: codex
- trust_level: high
- evidence:
  - `python scripts/check_no_legacy_entrypoint_imports.py`
  - `python -m unittest tests.api.test_entrypoint_dispatcher tests.api.test_frontend_api_routing tests.api.test_command_queue_foundation tests.api.test_runtime_execution tests.services.test_runtime_context_job tests.services.test_pipeline_runtime tests.services.test_sync_source_hash_gate tests.services.test_legacy_store_write_job tests.services.test_planner_pipeline_job tests.services.test_planner_setup_job tests.services.test_source_switch_job -v`
- result:
  - guard passed: `legacy_entrypoint_imports_check=ok`
  - targeted routing/runtime/legacy-reference tests passed
  - `index.py` now imports only `build_app_context` and `IndexDispatcher`
