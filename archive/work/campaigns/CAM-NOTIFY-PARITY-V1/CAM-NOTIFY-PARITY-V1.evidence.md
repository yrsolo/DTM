# Evidence - CAM-NOTIFY-PARITY-V1

## Trust Gate
- source: `src/notify/*`, `src/entrypoints/runtime/planner_runtime_entry.py`, `core/reminder.py`, `src/snapshot_engine/*`
- last_verified_at: 2026-03-07
- verified_by: codex
- trust_level: high
- evidence:
  - `src/notify/usecase.py` currently does generic status/window grouping and is not milestone day parity.
  - `src/notify/formatter.py` currently emits simplified per-owner list only.
  - `src/notify/telegram_sender.py` currently has no vacation/routing/retry/error counters.
  - runtime (`planner_runtime_entry.py`) currently returns minimal reminder summary and does not surface delivery/enhancement counters.
  - legacy reference behavior is in `core/reminder.py`:
    - today + next workday selection,
    - stage filtering via `filter_stages`,
    - LLM enhance fallback,
    - vacation/chat checks,
    - retry/backoff/classification/dedup counters.

## Drift Notes
- Previous CAM (`CAM-NOTIFY-MODULE-V1`) delivered skeleton notify module, not full business parity.
- Current task is parity restoration without reintroducing legacy runtime dependencies.

## Verification Checklist (pending)
- [x] people snapshot stored and loaded from snapshot contour.
- [x] reminder selection parity (today + next workday milestones).
- [x] formatter parity sections (today + next workday).
- [x] delivery parity checks and counters.
- [x] structured runtime response for reminder modes.
- [x] tests added and green.

## 2026-03-07 implementation evidence
- Added people snapshot primitives:
  - `PersonView`, `PeopleSnapshot` in `src/snapshot_engine/model.py`
  - `PeopleStore` protocol in `src/snapshot_engine/interfaces.py`
  - `S3PeopleStore` and `prefix_people` key wiring in `src/snapshot_engine/stores/s3_store.py`
  - people serialization in `src/snapshot_engine/serialization.py`
  - `PeopleSnapshotUpdater` in `src/snapshot_engine/update_job.py`
- Snapshot engine update now refreshes people snapshot together with task snapshots.
- Notify parity rewritten in `src/notify/*`:
  - today + next workday milestone selection
  - draft formatter with stage filtering
  - async LLM enhancement with fallback counters
  - delivery checks (person/chat/vacation/test-chat) + retry/backoff/classification + dedup
- Runtime integration:
  - `src/entrypoints/runtime/planner_runtime_entry.py` returns structured reminder counters for `reminder_v2`, `reminders-only`, `morning`.
  - test contour enforces test-chat delivery (`env=test` or mode `test`).
- Config additions:
  - `runtime.snapshot_engine.prefix_people`
  - `runtime.notify.*` typed settings
- Test evidence:
  - `python -m unittest tests.notify.test_reminder_v2_selection tests.notify.test_reminder_v2_formatter tests.notify.test_reminder_v2_delivery tests.notify.test_reminder_v2_llm tests.snapshot_engine.test_people_snapshot tests.snapshot_engine.test_update_job -v` -> OK
  - `python -m unittest tests.api.test_runtime_execution tests.services.test_pipeline_runtime tests.api.test_frontend_api_routing -v` -> OK
