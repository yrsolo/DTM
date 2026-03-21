# CAM-2026-03-21-CORE-ROOT-UNIFICATION-V1 Evidence

## Trust Gate

- source: current `core/` tree, `src/core/` tree, and active import graph
  - last_verified_at: `2026-03-21`
  - verified_by: `Codex`
  - evidence:
    - `Get-ChildItem core -Recurse -File`
    - `Get-ChildItem src/core -Recurse -File`
    - `rg -n "from core\\.|import core\\.|\\bcore\\.[A-Za-z_]" src tests agent scripts README.md docs work .github`
  - trust_level: `high`
  - notes: the split is real, not documentary drift: active runtime code, tests, and maintained smokes still import the root `core/` package, while `src/core/` already exists as the intended domain home.

## Active Tasks

- [x] move legacy root-domain files under `src/core/`
- [x] rewrite active imports from `core.*` to `src.core.*`
- [x] remove the tracked root `core/` package
- [x] strengthen guardrails against root `core/` resurrection
- [x] verify targeted runtime/test contour

## Iteration Notes

- campaign opened after owner decision: keep everything active under `src/`; root `core/` is stale and must be dissolved rather than preserved as a compatibility alias.
- root `core/` was dissolved as an active Python package:
  - migrated tracked files now live under `src/core/*`
  - active runtime/test/agent/local-tool imports were rewritten from `core.*` to `src.core.*`
  - the old root now survives only as local `__pycache__` noise after test runs, not as tracked code
- active files restored from `HEAD` before import rewrites where the first mechanical migration introduced mojibake in Russian literals; the final diff keeps import-path changes without carrying that accidental text corruption forward.
- updated active guardrails:
  - `test_active_code_does_not_import_root_core_package`
  - `test_root_core_package_does_not_exist_as_tracked_python_root`
- targeted verification stayed green:
  - `python scripts/check_no_legacy_entrypoint_imports.py`
  - `python -m unittest tests.architecture.test_guardrails_v0 tests.architecture.test_target_skeleton_imports tests.entrypoints.test_import_safety tests.api.test_frontend_api_v2_payload tests.core.test_timing_year_modes tests.services.test_readmodel_enums tests.test_task_query_contract tests.contexts.snapshot.test_sheets_normalized_source -v`
- after dissolving the root package, the internal cleanup phase removed the loudest non-domain shelves from `src/core/`:
  - `api_payload_v2.py` -> `src/contexts/access_api/internal/frontend_payload_v2.py`
  - `group_query.py` -> `src/contexts/telegram_interaction/internal/group_query_text.py`
  - `sheet_renderer.py` -> `src/contexts/rendering/internal/service_sheet_renderer.py`
  - `render_contracts.py` removed as dead code
  - `read_model.py` -> `src/platform/artifacts/read_model.py`
  - `schema_snapshot.py` -> `src/platform/artifacts/schema_snapshot.py`
  - `fixture_bundle.py` -> `src/platform/artifacts/fixture_bundle.py`
  - `reminder.py` -> `agent/support/reminder_runtime.py`
  - `adapters.py` -> `src/platform/contracts/adapters.py`
  - `reminder_policy.py` -> `src/platform/policies/reminder_policy.py`
- aligned active imports and maintained smokes/tests with those new homes:
  - browser payload tests now read through `src.contexts.access_api.internal.frontend_payload_v2`
  - local/prototype artifact tooling now reads through `src.platform.artifacts.*`
  - reminder smokes now import `agent.support.reminder_runtime`
  - group query smoke now imports `src.contexts.telegram_interaction.internal.group_query_text`
- follow-up verification for the narrowed core contour stayed green:
  - `python -m unittest tests.api.test_frontend_api_v2_payload tests.services.test_readmodel_enums -v`
  - `python -m unittest tests.api.test_frontend_api_v2_payload tests.services.test_readmodel_enums tests.test_task_query_contract tests.core.test_timing_year_modes tests.architecture.test_guardrails_v0 tests.architecture.test_target_skeleton_imports tests.entrypoints.test_import_safety tests.contexts.snapshot.test_sheets_normalized_source -v`
  - `python -m agent.smokes.group_query_smoke`
  - `python -c "from src.contexts.rendering.internal.service_sheet_renderer import ServiceSheetRenderAdapter; print('service_sheet_renderer_import_ok')"`
  - `python -c "from agent.support.reminder_runtime import Reminder, FallbackChatAdapter; print('reminder_runtime_import_ok')"`
- next blocker is no longer preserved non-domain helper shelves; it is the remaining shared query/timing slice inside `src/core/`:
  - `task_query_adapter.py`
  - `task_query_contract.py`
  - `task_repository_contract.py`
  - `task_timing_processor.py`
  - plus the still-shared row/error contracts in `contracts.py` and `errors.py`
- that remaining slice is no longer a safe cleanup-only move, because it serves multiple live consumers across `access_api`, `snapshot`, `platform.integrations.google_sheets`, and agent/tooling flows.
