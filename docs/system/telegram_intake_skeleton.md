# Telegram Intake Skeleton

## Purpose

Source of truth for future Telegram webhook intake that only parses updates and enqueues internal commands.

## Goal

Make Telegram integration thin, safe, and operationally transparent:
- webhook only
- minimal `allowed_updates`
- secret token validation
- no heavy work inside webhook handler
- enqueue-only behavior

## Non-goals

- No full Telegram runtime rollout in queue foundation v1
- No business execution inside webhook path
- No bot framework ownership of application architecture

## Policy

- Transport mode: webhook only
- Security: require `X-Telegram-Bot-Api-Secret-Token`
- Privacy mode: preserve where possible
- Allowed updates start with:
  - `message`
  - `callback_query`
  - optionally `my_chat_member`

## Future Module Tree

- `src/telegram/webhook.py`
- `src/telegram/parser.py`
- `src/telegram/sender.py`

## Module Contracts

## `src/telegram/webhook.py`
- Verify secret token
- Parse incoming update
- Map update to internal `Command`
- Enqueue command
- Return `200` quickly
- Must not call reminder/render/snapshot work directly

## `src/telegram/parser.py`
- Thin parser over Telegram update JSON
- Detect supported command/action
- Return normalized parser result
- No business selection logic

## `src/telegram/sender.py`
- Telegram transport adapter for worker jobs only
- No webhook parsing logic

## Current Touchpoints

- [src/entrypoints/http/group_query_handler.py](n:/PROJECTS/python/SCRIPT/DTM/src/entrypoints/http/group_query_handler.py)
- [src/adapters/telegram.py](n:/PROJECTS/python/SCRIPT/DTM/src/adapters/telegram.py)
- [src/notify/job.py](n:/PROJECTS/python/SCRIPT/DTM/src/notify/job.py)
- [src/entrypoints/http/info_handler.py](n:/PROJECTS/python/SCRIPT/DTM/src/entrypoints/http/info_handler.py)

## Future Route Integration

Telegram webhook should eventually become an explicit HTTP route handled separately from generic runtime mode execution.

Target behavior:
1. receive webhook
2. validate token
3. parse update
4. map to internal command
5. enqueue command
6. return `200 OK`

## Command Mapping

Future supported mappings:
- group mention / deadlines request -> `group_query_reply`
- admin bot command -> `update_snapshot`
- admin bot command -> `send_reminders`

## Ops Observability

`/info` should later expose:
- webhook URL
- allowed updates
- max connections
- pending updates
- last error date/message

This is future work, not part of queue foundation v1.

## Forbidden Shortcuts

- No heavy business logic in webhook handler
- No direct Sheets reads in webhook path
- No direct reminder/render execution in webhook path
- No polling mode
