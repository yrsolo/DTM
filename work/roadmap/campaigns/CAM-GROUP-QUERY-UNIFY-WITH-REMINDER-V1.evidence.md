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
