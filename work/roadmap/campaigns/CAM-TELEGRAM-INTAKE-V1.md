# CAM-TELEGRAM-INTAKE-V1

## Goal

Introduce thin Telegram webhook intake that validates, parses, and enqueues commands without executing business logic inline.

## Scope

- webhook-only policy
- secret token validation
- `allowed_updates` policy
- enqueue-only command mapping
- operational webhook diagnostics

## Non-goals

- no polling mode
- no heavy work in webhook
- no broad Telegram bot framework ownership over app architecture

## Implementation Skeleton Reference

- Primary implementation skeleton: `docs/system/telegram_intake_skeleton.md`
- Current trust level: medium
- Current touchpoints:
  - `src/telegram/webhook.py`
  - `src/telegram/parser.py`
  - `src/jobs/group_query_reply_job.py`
  - `src/entrypoints/http/group_query_handler.py`
  - `src/adapters/telegram.py`
  - `src/notify/job.py`
  - `src/entrypoints/http/info_handler.py`
- Depends on: `CAM-QUEUE-FOUNDATION-ON-CF-V1`
- Forbidden shortcuts:
  - no direct reminder/render/snapshot execution in webhook
  - no polling fallback

## Phases

1. Telegram parser/sender adapters
2. Webhook security contour
3. Command mapping
4. Ops visibility

## DoD

- webhook path validates and enqueues only
- heavy business logic stays out of webhook
- `/info` can expose webhook health metadata
- worker executes `group_query_reply` after enqueue instead of synchronous webhook reply
