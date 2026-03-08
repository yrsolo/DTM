# Group Query Unification Skeleton

## Purpose

Source of truth for future migration of Telegram group query to the same task selection contour used by reminders.

## Current Problems

- current group query replies synchronously in webhook/request path
- handler still uses `pandas`
- selection logic duplicates reminder-like logic instead of sharing one use-case

Current touchpoint:
- [src/entrypoints/http/group_query_handler.py](n:/PROJECTS/python/SCRIPT/DTM/src/entrypoints/http/group_query_handler.py)

## Goal

Make group query a specialized formatting/transport case over the same selection logic as reminders.

## Target Architecture

- shared selection path:
  - `ReminderUseCase.select_tasks(...)` or extracted `ReminderSelectionService`
- separate formatter:
  - `GroupQueryFormatter`
- separate transport:
  - Telegram group reply sender

## Required Refactor Shape

1. parse requester / request type
2. call shared selection path
3. format response with group-query formatter
4. send reply

No data filtering logic should remain inside handler after migration.

## Sync vs Async Rollout

Initial migration can keep group query synchronous if needed for UX parity.

Later async option:
- Telegram webhook enqueues `group_query_reply`
- worker sends reply later as separate message

This async decision must be explicit in the future CAM, not assumed here.

## Current Touchpoints

- [src/entrypoints/http/group_query_handler.py](n:/PROJECTS/python/SCRIPT/DTM/src/entrypoints/http/group_query_handler.py)
- [src/notify/usecase.py](n:/PROJECTS/python/SCRIPT/DTM/src/notify/usecase.py)
- [src/adapters/telegram.py](n:/PROJECTS/python/SCRIPT/DTM/src/adapters/telegram.py)
- [src/snapshot_engine/engine.py](n:/PROJECTS/python/SCRIPT/DTM/src/snapshot_engine/engine.py)

## Desired End State

- no `pandas` in group query handler
- no duplicate milestone/window selection logic
- same task universe for reminder and group query under equal conditions

## Future Formatter Split

- `ReminderFormatter` for personal reminders
- `GroupQueryFormatter` for group replies

## Forbidden Shortcuts

- No direct business filtering in HTTP handler
- No second selection engine just for group query
- No silent drift from reminder semantics
