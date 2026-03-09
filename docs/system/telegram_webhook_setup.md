# Telegram Webhook Setup

## Recommended mode

Webhook only.

## Handler behavior

Webhook must:

1. verify secret token
2. parse Telegram update into typed DTO
3. route DTO to internal command intent
4. enqueue internal command
5. return quickly

Webhook must not:

- refresh snapshot inline
- render sheets inline
- send reminders inline
- query Google Sheets inline

## Current path

Current webhook path is configured by:

- `runtime.telegram.webhook_path`

Default is `/telegram`.

## Security

- validate header `X-Telegram-Bot-Api-Secret-Token`
- keep `allowed_updates` minimal
- keep privacy mode enabled unless a real use-case requires more visibility

## Admin visibility

`/info?format=json` should expose:

- webhook path
- webhook URL
- `allowedUpdates`
- `maxConnections`
- `secretRequired`
- `secretConfigured`
