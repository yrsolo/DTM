# CAM-2026-03-22-ACTIVE-DOCS-RUNTIME-DRIFT-FIX-V1 - Evidence

## Trust Gate

- source: current runnable code in `src/contexts/access_api/**`, `src/contexts/snapshot/**`, `src/platform/runtime/timer_pipeline.py`, `src/entrypoints/http/router.py`
- last_verified_at: 2026-03-22
- verified_by: Codex
- evidence:
  - read `src/entrypoints/http/router.py`
  - read `src/contexts/access_api/application/browser_read_api.py`
  - read `src/contexts/access_api/internal/primary_task_list_read_api.py`
  - read `src/contexts/access_api/application/primary_task_list_read_service.py`
  - read `src/contexts/access_api/internal/operational_info_read_api.py`
  - read `src/contexts/snapshot/module.py`
  - read `src/contexts/snapshot/internal/runtime_binding.py`
  - read `src/platform/runtime/timer_pipeline.py`
- trust_level: high
- notes: active docs were treated as drift candidates until checked against runnable code

## Execution Notes

- started: 2026-03-22
- completed: 2026-03-22
- scope: active docs only; no behavioral/runtime change intended
- updated active docs:
  - `docs/architecture/snapshot-engine/architecture.md`
  - `docs/architecture/runtime/entrypoints.md`
  - `docs/architecture/runtime/dataflow.md`
  - `docs/architecture/runtime/architecture.md`
  - `docs/integrations/attachments/backend-flow.md`
  - `docs/architecture/future/command-queue-skeleton.md`
- verification:
  - `rg -n "frontend_v2_handler\\.py|src/services/timer_pipeline\\.py|task_attachment_read_handler\\.py|InfoHandler\\b|FrontendV2Handler\\b|PeopleSnapshotHandler\\b|TaskAttachmentReadHandler\\b" docs`
  - `python -m unittest tests.architecture.test_guardrails_v0 tests.entrypoints.test_import_safety tests.contexts.access_api.test_frontend_api_routing tests.contexts.access_api.test_info_observability tests.contexts.access_api.test_task_attachment_read_api -v`
- result:
  - active docs no longer point at removed handler-era paths
  - verification contour green (`89 tests`, `OK`)
