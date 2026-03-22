# CAM-2026-03-22-TELEGRAM-INTERACTION-SURFACE-V1 Plan

## Trust Gate
- source: `src/contexts/telegram_interaction/public.py`, `src/contexts/telegram_interaction/internal/job_runner.py`, `src/entrypoints/http/router.py`
- last_verified_at: 2026-03-22
- verified_by: Codex
- evidence:
  - `rg -n "from src\\.contexts\\.telegram_interaction\\.public import|get_update_parser\\(|get_command_router\\(|get_webhook_handler\\(|get_snapshot_read_api\\(|get_usecase\\(|get_group_query_formatter\\(|get_sender\\(|make_group_query_request\\(|get_group_query_reply_job\\(" src tests`
  - direct reads of active telegram interaction runtime files
- trust_level: high
- notes:
  - The helper catalog in `telegram_interaction.public` still sits on live webhook and group-query runtime paths.

## Phases

### P01 - Canonical Telegram Interaction Surface
- `CAM-2026-03-22-TELEGRAM-INTERACTION-SURFACE-V1-P01-T001` Add one application-owned telegram interaction API for webhook and group-query reply assembly.
- `CAM-2026-03-22-TELEGRAM-INTERACTION-SURFACE-V1-P01-T002` Repoint webhook wiring and group-query reply execution to that API instead of helper-by-helper public imports.
- `CAM-2026-03-22-TELEGRAM-INTERACTION-SURFACE-V1-P01-T003` Shrink `telegram_interaction.public` to canonical interaction surface exports plus queue command handlers.

### P02 - Verification And Tracking
- `CAM-2026-03-22-TELEGRAM-INTERACTION-SURFACE-V1-P02-T001` Run the targeted telegram/router/guardrail test contour.
- `CAM-2026-03-22-TELEGRAM-INTERACTION-SURFACE-V1-P02-T002` Close out local tracking and archive the completed campaign record.
