# DTM-179: Stage 17 group query smoke

## Context
- Group query logic needs deterministic local checks.

## Goal
- Add smoke script covering command/mention parsing and response rendering.

## Non-goals
- External Telegram API integration test.

## Plan
1. Create smoke script with fake tasks and fake updates.
2. Assert parser and render behavior.
3. Add smoke run evidence to Stage docs/context.

## Checklist (DoD)
- [x] `agent/group_query_smoke.py` added.
- [x] Smoke checks pass locally.
- [x] Existing reminder smoke remains green.

## Work log
- 2026-02-28: Added smoke script and executed pass run.

## Links
- `agent/group_query_smoke.py`
