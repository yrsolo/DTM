# Reserve Capabilities

## Telegram interaction

`telegram_interaction` is kept as a reserve capability, not as an active architecture center.

## What must stay supported

- webhook intake still works
- `group_query_reply` still works
- Telegram reminder delivery channel remains supported where already used

## What is not required right now

- deep redesign for ideal Telegram architecture
- Telegram-first product shaping
- letting Telegram drive reminder or main browser read-side decisions

## Maintenance rule

Changes to Telegram should be evaluated by one question:

does this preserve reserve capability without distorting the main read-side and active reminder path?
