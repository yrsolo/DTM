# CAM-2026-03-20-MODULE-FIRST-RECOVERY-V1 Evidence

## Trust gate
- source: current module-first draft, active recovery docs, attachment publication scenario, current code map, module docs
- last_verified_at: 2026-03-20
- verified_by: Codex
- evidence:
  - `agent/intructions/mew_plan2.md`
  - `docs/integrations/attachments/frontend-card-publication.md`
  - `docs/architecture/recovery/README.md`
  - `docs/architecture/runtime/module-map.md`
  - `src/entrypoint/handler.py`
  - `index.py`
- trust_level: high
- notes:
  - the new canon is stricter than the predecessor and changes the active reading priority toward the primary task-list read-model
  - the first code-facing execution wave must be a delta audit against this new canon

## Completed Tasks
- [x] `CAM-2026-03-20-MODULE-FIRST-RECOVERY-V1-P01-T001`
- [x] `CAM-2026-03-20-MODULE-FIRST-RECOVERY-V1-P01-T002`
- [x] `CAM-2026-03-20-MODULE-FIRST-RECOVERY-V1-P01-T003`
- [x] `CAM-2026-03-20-MODULE-FIRST-RECOVERY-V1-P01-T004`
- [x] `CAM-2026-03-20-MODULE-FIRST-RECOVERY-V1-P02-T001`
- [x] `CAM-2026-03-20-MODULE-FIRST-RECOVERY-V1-P02-T002`
- [x] `CAM-2026-03-20-MODULE-FIRST-RECOVERY-V1-P02-T003`
- [x] `CAM-2026-03-20-MODULE-FIRST-RECOVERY-V1-P02-T004`
- [x] `CAM-2026-03-20-MODULE-FIRST-RECOVERY-V1-P03-T001`
- [x] `CAM-2026-03-20-MODULE-FIRST-RECOVERY-V1-P04-T001`
- [x] `CAM-2026-03-20-MODULE-FIRST-RECOVERY-V1-P07-T001`
- [x] `CAM-2026-03-20-MODULE-FIRST-RECOVERY-V1-P07-T002`
- [x] `CAM-2026-03-20-MODULE-FIRST-RECOVERY-V1-P10-T001`
- [x] `CAM-2026-03-20-MODULE-FIRST-RECOVERY-V1-P10-T002`

## Verification
- Command:
  - `Get-Content agent/intructions/mew_plan2.md`
  - `Get-Content docs/architecture/recovery/README.md`
  - `Get-Content docs/integrations/attachments/frontend-card-publication.md`
  - `Get-Content index.py`
  - `Get-Content src/entrypoint/handler.py`
  - `Get-Content src/platform/bootstrap.py`
  - `Get-Content src/entrypoints/http/router.py`
  - `Get-Content src/contexts/access_api/module.py`
  - `Get-Content src/contexts/attachments/module.py`
  - `Get-Content src/platform/runtime/queue_bootstrap.py`
  - `rg -n "src\\.jobs|HttpRouter|get_http_shell|get_worker_shell|get_trigger_shell" index.py src tests`
  - `python -m unittest tests.contexts.attachments.test_attach_task_file_job tests.contexts.attachments.test_delete_task_attachment_job tests.contexts.attachments.test_cleanup_task_attachments_job tests.contexts.attachments.test_generate_attachment_preview_job tests.contexts.reminders.test_send_reminders_job tests.contexts.telegram_interaction.test_group_query_reply_job tests.architecture.test_guardrails_v0 tests.entrypoints.test_import_safety -v`
  - `python -m unittest tests.entrypoints.test_planner_runtime_entry tests.api.test_telegram_webhook_handler tests.contexts.rendering.test_render_v2 tests.contexts.rendering.test_designers_render_v2 tests.api.test_frontend_api_routing tests.api.test_info_observability tests.api.test_task_attachment_read_handler -v`
  - `rg -n "from src\\.jobs|import src\\.jobs|src\\.jobs\\." src/contexts src/platform src/entrypoint src/entrypoints`
- Result:
- the new module-first canon introduces a stricter stance than the previous recovery set
- attachment publication and the primary task-list read-model are now explicit governing scenarios
- attachment readiness is treated as an operational signal that leads to task-list refetch, not as the canonical browser read artifact
- Telegram is now treated as reserve capability, not a co-equal active architecture center
- generic `src/jobs/*` no longer acts as an active execution center; active runtime and contexts now obtain runners through owning modules, and the compatibility root is removed
- browser-facing read routes are now composed inside `access_api` via `BrowserRoutesHandler`, so `HttpRouter` no longer owns the frontend/info/people/attachment-read fanout directly
- queue/worker orchestration is now bound through module-owned command handler maps instead of direct `src.jobs` fanout in platform bootstrap
- attachment preview converter assembly moved out of `app/bootstrap.py` into the owning `attachments` module; bootstrap now carries raw runtime inputs instead of building the domain adapter directly
- active entrypoints/contexts now use platform-owned `command_runtime` capability instead of reading `command_queue_producer`, `job_status_store`, and `command_worker` directly from the generic deps bag
- `src/snapshot_engine/*` is removed as a top-level implementation island; the read-side engine now lives under `src/contexts/snapshot/internal/engine/*`
- compatibility-only `src/jobs/*` is removed from the active tree
- active test layout now follows module ownership under `tests/contexts/*`; old runtime-oriented test roots no longer carry Python files

## Notes
- `CAM-2026-03-20-ARCHITECTURE-RECOVERY-V1` remains closed as phase-one precedent.
- Structured delta audit is now recorded in `delta-audit.md`.
- Active runtime and active test layout now both follow module-first ownership; remaining historical path names in `work/archive/**` are preserved only as campaign evidence.
