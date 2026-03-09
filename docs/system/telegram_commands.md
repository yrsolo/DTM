# Telegram Commands

## Purpose

Telegram is an intake channel, not a business-logic host.

Webhook flow:

- parse -> route -> enqueue -> return

## Supported internal Telegram command names (v1)

- `group_deadlines_me`
- `group_tasks_me`
- `refresh_snapshot`
- `send_statuses`
- `render_timeline`

## Mapping to internal queue commands

- `group_deadlines_me` -> `group_query_reply`
- `group_tasks_me` -> `group_query_reply`
- `refresh_snapshot` -> `update_snapshot`
- `send_statuses` -> `send_reminders`
- `render_timeline` -> `render_timeline_sheet`

## Current scope

Current router intentionally focuses on async command mapping.

Immediate reply commands like `/help` or `/status` may be added later, but they are not required for the current contour.
