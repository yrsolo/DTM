# Evidence - CAM-TELEGRAM-INTAKE-V1

## Trust Gate

- source:
  - `src/entrypoints/http/group_query_handler.py`
  - `src/entrypoints/http/router.py`
  - `src/commands/types.py`
  - `src/worker/dispatcher.py`
  - `src/adapters/telegram.py`
  - `src/entrypoints/http/info_handler.py`
  - `docs/system/config.md`
- last_verified_at: 2026-03-08
- verified_by: codex
- trust_level: high
- evidence:
  - Current Telegram webhook behavior is still synchronous: `src/entrypoints/http/group_query_handler.py` parses update, runs selection, formats, and sends reply inline.
  - Queue foundation is live in code and test env: command types, worker dispatcher, status store, and admin enqueue endpoints already exist.
  - Router still mounts Telegram behavior through generic HTTP route handling; there is no dedicated secret-validated webhook handler.
  - `/info` currently has queue diagnostics but no webhook config/health block.

## Notes

- Depends on `CAM-QUEUE-FOUNDATION-ON-CF-V1`.
- Primary implementation source doc: `docs/system/telegram_intake_skeleton.md`
- implementation_result_2026-03-08:
  - `src/telegram/webhook.py` now validates Telegram secret token and enqueues commands instead of executing business logic inline.
  - `src/telegram/parser.py` maps group `/tasks` and `/deadlines` requests to `group_query_reply`, and safe private default-chat commands to `update_snapshot` / `send_reminders`.
  - `src/jobs/group_query_reply_job.py` executes the actual reply using snapshot-backed `ReminderUseCase.select()` and `GroupQueryFormatter`.
  - `/info?format=json` now exposes Telegram webhook config block (`webhookPath`, `webhookUrl`, `allowedUpdates`, `maxConnections`, `secretConfigured`).
- tests_verified:
  - `python -m unittest tests.api.test_telegram_webhook_handler -v`
  - `python -m unittest tests.jobs.test_group_query_reply_job -v`
  - `python -m unittest tests.api.test_frontend_api_routing -v`
  - `python -m unittest tests.api.test_command_queue_foundation -v`
