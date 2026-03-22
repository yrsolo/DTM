# Telegram Webhook

## Recommended mode

Webhook only.

## Что должен делать webhook

1. проверить secret token;
2. распарсить Telegram update в typed DTO;
3. сопоставить update с internal command intent;
4. enqueue command;
5. быстро вернуть ответ.

## Чего webhook не должен делать

- refresh snapshot inline;
- render sheets inline;
- send reminders inline;
- читать Google Sheets inline.

## Текущий path

Текущий webhook path задаётся через `runtime.telegram.webhook_path`.

## Security

- проверять `X-Telegram-Bot-Api-Secret-Token`;
- держать `allowed_updates` минимальным;
- не расширять Telegram contour без реальной product-необходимости.
