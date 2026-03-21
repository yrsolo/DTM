# CAM-2026-03-21-SNAPSHOT-MODULE-SURFACE-V1 Evidence

## Trust Gate

- source: current active snapshot read/update surface
  - last_verified_at: `2026-03-21`
  - verified_by: `Codex`
  - evidence:
    - `src/contexts/snapshot/public.py`
    - `src/contexts/snapshot/module.py`
    - `src/contexts/snapshot/internal/engine/*`
  - trust_level: `high`
  - notes: direct code inspection confirmed the smell is real; the first bounded cut is to remove direct shortcut wrappers and force consumers through snapshot capabilities.

## Active Tasks

- [x] verify the smallest safe contract-first cut
- [x] decide whether the first move belongs in `module.py`, `public.py`, or new `application/*`
- [x] execute only one bounded structural cut
- [x] record whether the smell shrank enough to continue or became a larger redesign stage

## Iteration Notes

- first cut executed:
  - removed direct shortcut wrappers from `src/contexts/snapshot/public.py`
  - removed duplicate direct engine passthrough methods from `src/contexts/snapshot/module.py`
  - moved active consumers to capability contracts in:
    - `src/entrypoints/http/admin_queue_handler.py`
    - `src/entrypoints/http/group_query_tasks_loader.py`
- verification:
  - `python -m unittest tests.architecture.test_guardrails_v0 tests.entrypoints.test_import_safety tests.api.test_command_queue_foundation tests.contexts.telegram_interaction.test_group_query_reply_job tests.contexts.reminders.test_reminder_v2_selection tests.contexts.rendering.test_render_v2 -v`
  - `rg -n "from src\\.contexts\\.snapshot\\.public import .*get_prep_snapshot|from src\\.contexts\\.snapshot\\.public import .*query_frontend_v2|from src\\.contexts\\.snapshot\\.public import .*get_people_snapshot|from src\\.contexts\\.snapshot\\.public import .*get_raw_snapshot|from src\\.contexts\\.snapshot\\.public import .*get_response_cache_store" src tests`

## Current Assessment

- smell shrank: direct shortcut surface is gone, and active consumers now read snapshot through capability contracts.
- second cut executed:
  - moved capability classes out of `src/contexts/snapshot/module.py` into `src/contexts/snapshot/application/capabilities.py`
  - reduced `SnapshotModule` to a boring factory over capability contracts instead of an `engine()`-centered surface
  - cut the update-path cycle by moving `UpdateSnapshotJob` to `SnapshotUpdateCapability` directly instead of going back through `snapshot.public`
- second-cut verification:
  - `python -m unittest tests.architecture.test_guardrails_v0 tests.entrypoints.test_import_safety tests.api.test_command_queue_foundation tests.contexts.telegram_interaction.test_group_query_reply_job tests.contexts.reminders.test_reminder_v2_selection tests.contexts.rendering.test_render_v2 tests.contexts.attachments.test_attach_task_file_job tests.contexts.attachments.test_delete_task_attachment_job tests.contexts.attachments.test_generate_attachment_preview_job -v`
  - `rg -n "from src\\.contexts\\.snapshot\\.public import get_update_capability|\\.engine\\(|class Snapshot(Read|Query|Attachment|Update)Capability" src tests`
- third cut executed:
  - renamed `Snapshot*Capability` classes to `Snapshot*Api` and moved the canonical module grammar to `read_api/query_api/attachment_api/update_api`
  - switched the most visible active consumers from `src.contexts.snapshot.public` to `src.contexts.snapshot.module`
  - renamed downstream seams away from `snapshot_capability` / `snapshot_engine` wording in `access_api`, `attachments`, `reminders`, `rendering`, `telegram_interaction`, `timer_pipeline`, and planner runtime entry
  - updated guardrails and active tests to treat `src.contexts.snapshot.module` as the canonical cross-context seam
- third-cut verification:
  - `python -m unittest tests.api.test_frontend_api_routing tests.api.test_info_observability tests.api.test_command_queue_foundation tests.contexts.attachments.test_attach_task_file_job tests.contexts.attachments.test_delete_task_attachment_job tests.contexts.attachments.test_cleanup_task_attachments_job tests.contexts.attachments.test_generate_attachment_preview_job tests.contexts.reminders.test_send_reminders_job tests.contexts.telegram_interaction.test_group_query_reply_job tests.services.test_pipeline_runtime tests.entrypoints.test_planner_runtime_entry tests.architecture.test_guardrails_v0 tests.entrypoints.test_import_safety -v`
  - `rg -n "get_snapshot_read_capability|get_attachment_snapshot_capability|get_snapshot_query_capability|get_snapshot_capability\\b|Snapshot(Read|Query|Attachment|Update)Capability" src tests`
- fourth cut executed:
  - introduced `src/contexts/snapshot/internal/runtime_binding.py` as the shared runtime bundle for module APIs and engine assembly
  - moved `SnapshotReadApi` and `SnapshotQueryApi` off full `build_snapshot_engine(...)` usage onto direct stores/query-engine from that runtime bundle
  - moved `SnapshotUpdateApi` off engine-backed update and onto direct runtime job factories
  - reduced `SnapshotAttachmentApi` engine usage to mutation methods only; read/cache/store access now comes directly from the runtime bundle
- fourth-cut verification:
  - `python -m unittest tests.contexts.snapshot.test_query_engine tests.contexts.snapshot.test_update_job tests.api.test_frontend_api_routing tests.api.test_info_observability tests.api.test_command_queue_foundation tests.contexts.attachments.test_attach_task_file_job tests.contexts.attachments.test_delete_task_attachment_job tests.contexts.attachments.test_cleanup_task_attachments_job tests.contexts.attachments.test_generate_attachment_preview_job tests.contexts.reminders.test_send_reminders_job tests.contexts.telegram_interaction.test_group_query_reply_job tests.services.test_pipeline_runtime tests.entrypoints.test_planner_runtime_entry tests.architecture.test_guardrails_v0 tests.entrypoints.test_import_safety -v`
  - `python -m unittest tests.contexts.snapshot.test_update_job tests.api.test_command_queue_foundation tests.contexts.attachments.test_attach_task_file_job tests.contexts.attachments.test_delete_task_attachment_job tests.contexts.attachments.test_cleanup_task_attachments_job tests.contexts.attachments.test_generate_attachment_preview_job tests.services.test_pipeline_runtime tests.architecture.test_guardrails_v0 tests.entrypoints.test_import_safety -v`
  - `rg -n "_bound_engine\\(|build_snapshot_engine_from_runtime|build_snapshot_engine\\(" src/contexts/snapshot src/contexts/attachments src/services tests`
- smell still alive:
  - the active `snapshot` surface is no longer broadly engine-backed, but attachment mutation methods in `SnapshotAttachmentApi` still delegate through `_bound_engine()` and `build_snapshot_engine_from_runtime(...)`
  - this is no longer a naming/seam smell; it is a concrete design choice about whether attachment mutation logic should become its own reusable module-level service instead of living in `SnapshotEngine`
- next honest move is a dedicated attachment-mutation extraction:
  - either introduce a reusable attachment projection service that both `SnapshotAttachmentApi` and `SnapshotEngine` can share
  - or accept `SnapshotEngine` as the internal owner of attachment mutation semantics while keeping it out of the active read/update/query surface
