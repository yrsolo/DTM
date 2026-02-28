# DTM-178: Stage 17 group query runtime path

## Context
- Cloud handler currently processes planner runs and healthcheck only.
- Telegram group updates need a dedicated handling path.

## Goal
- Add runtime handling for group commands/mentions returning tasks/deadlines.

## Non-goals
- Long-polling bot mode.
- Personalized access controls.

## Plan
1. Add parser/renderer module for group query logic.
2. Route Telegram HTTP updates in `index.py`.
3. Reply to same group chat via `TelegramNotifier`.

## Checklist (DoD)
- [x] New helper module added.
- [x] `index.py` handles group query path and bypasses planner run.
- [x] Fallback error response for query failures.

## Work log
- 2026-02-28: Added `core/group_query.py` and integrated it into `index.py`.

## Links
- `core/group_query.py`
- `index.py`
