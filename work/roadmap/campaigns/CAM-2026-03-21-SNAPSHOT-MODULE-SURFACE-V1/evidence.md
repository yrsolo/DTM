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
- [ ] record whether the smell shrank enough to continue or became a larger redesign stage

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
- smell still alive: `SnapshotModule` still centers on `build_snapshot_engine` and thin engine-bound capability proxies.
- next honest move is no longer another local wrapper deletion; it is a deeper contract-first redesign inside `src/contexts/snapshot/module.py`.
