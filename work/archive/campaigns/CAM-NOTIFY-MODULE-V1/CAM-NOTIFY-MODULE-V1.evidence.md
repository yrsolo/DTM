# CAM-NOTIFY-MODULE-V1.evidence

## Trust gate
- source: `src/notify/*`, `src/entrypoints/runtime/planner_runtime_entry.py`, `src/snapshot_engine/engine.py`
- last_verified_at: 2026-03-06
- verified_by: Codex agent
- trust_level: high
- evidence:
  - runtime path for `reminders-only` and `reminder_v2` verified in code.
  - no `core/*`, `pandas`, `GoogleSheetPlanner` imports in `src/notify`.

## Execution evidence
- implemented `ReminderUseCase` selection/grouping over `PrepSnapshot`.
- implemented `ReminderFormatter` and async `TelegramReminderSender`.
- wired runtime mode `reminder_v2` and aliased `reminders-only` to v2 notify path.
- added unit tests in `tests/notify/test_reminder_v2.py`.

## Verification
- `python -m unittest tests.notify.test_reminder_v2 -v` -> OK
- `python -m unittest tests.api.test_frontend_api_routing -v` -> OK
- `python scripts/check_no_legacy_imports.py` -> OK

