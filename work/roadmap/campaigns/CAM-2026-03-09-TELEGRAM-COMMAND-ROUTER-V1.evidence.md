# CAM-2026-03-09-TELEGRAM-COMMAND-ROUTER-V1 Evidence

## Trust gate

- source: active telegram runtime files
- last_verified_at: 2026-03-09
- verified_by: Codex
- evidence:
  - `src/telegram/parser.py`
  - `src/telegram/webhook.py`
  - `src/jobs/group_query_reply_job.py`
  - `src/notify/usecase.py`
- trust_level: high

## Delivered

- typed Telegram DTOs live in `src/telegram/model.py`
- command routing moved to `src/telegram/command_router.py`
- parser no longer owns queue-command mapping
- webhook remains secret-validated and enqueue-only

## Proof

- `tests/telegram/test_command_router.py`
- `tests/api/test_telegram_webhook_handler.py`
