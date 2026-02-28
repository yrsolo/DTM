# Stage 17 Group Query Smoke And Evidence

## Smoke checks
- `.venv\Scripts\python.exe -m compileall config core agent index.py`
- `.venv\Scripts\python.exe -m agent.group_query_smoke`
- `.venv\Scripts\python.exe -m agent.reminder_fallback_smoke`

## Added smoke script
- `agent/group_query_smoke.py`
  - validates parser for command and mention flows,
  - validates response rendering for personal tasks and team deadlines.

## Notes
- Smoke is deterministic and does not call Telegram API.
- Runtime path for real webhook updates is verified by code flow and local parser/render checks.
