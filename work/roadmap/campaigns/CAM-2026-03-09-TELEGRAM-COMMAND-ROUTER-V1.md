# CAM-2026-03-09-TELEGRAM-COMMAND-ROUTER-V1

## Goal

Make Telegram intake extensible without moving business logic back into webhook.

## Scope

- typed `ParsedTelegramUpdate`
- dedicated `TelegramCommandRouter`
- parser/router split
- webhook remains enqueue-only
- docs/tests

## Non-goals

- no heavy bot runtime
- no business logic inside webhook
- no queue bypass

## DoD

- parser and router are separate concerns
- webhook validates secret, parses, routes, enqueues, returns quickly
- group query remains worker-side and still uses reminder selection path
