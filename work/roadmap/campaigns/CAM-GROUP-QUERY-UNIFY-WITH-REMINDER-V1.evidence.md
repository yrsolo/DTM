# Evidence - CAM-GROUP-QUERY-UNIFY-WITH-REMINDER-V1

## Trust Gate

- source:
  - `src/entrypoints/http/group_query_handler.py`
  - `src/notify/usecase.py`
  - `src/snapshot_engine/engine.py`
- last_verified_at: 2026-03-08
- verified_by: codex
- trust_level: high
- evidence:
  - current group query handler parses Telegram payload, filters tasks, formats reply, and sends message in one place.
  - current handler still imports and uses `pandas`.
  - reminder selection already exists separately in `src/notify/usecase.py`.

## Notes

- Primary implementation source doc: `docs/system/group_query_unification_skeleton.md`
- execution_slice_2026-03-08:
  - move `CAM-GROUP-QUERY-UNIFY-WITH-REMINDER-V1` from planned to active
  - replace payload-shaped selection in `src/entrypoints/http/group_query_handler.py`
  - prove parity against `ReminderUseCase.select()` with `PrepSnapshot`-based tests
- implementation_result_2026-03-08:
  - `src/entrypoints/http/group_query_handler.py` now delegates selection to `ReminderUseCase.select()` and only parses Telegram group input, chooses formatter branch, and sends reply.
  - `src/notify/group_query_formatter.py` introduced dedicated team/deadlines formatting without reintroducing filtering logic.
  - `tests/api/test_group_query_snapshot_handler.py` now builds `PrepSnapshot` fixtures and proves that only today/next-workday milestone tasks are returned.
  - `index.py`, `src/jobs/render_timeline_job.py`, `src/jobs/render_designers_job.py`, `src/commands/yandex_mq.py`, and `src/worker/status_store.py` were tightened to lazy-load optional SDKs so routing tests do not fail on plain import.
- tests_verified:
  - `python -m unittest tests.api.test_group_query_snapshot_handler -v`
  - `python -m unittest tests.api.test_frontend_api_routing -v`
  - `python -m unittest tests.notify.test_reminder_v2_selection -v`
  - `python -m unittest tests.api.test_command_queue_foundation -v`
