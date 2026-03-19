# Telegram Interaction

## Purpose

`telegram_interaction` owns:
- Telegram webhook intake
- Telegram update parsing
- update-to-command mapping
- Telegram interaction flows for group/user replies

## Public facade expectation

Target context shape:

```text
src/contexts/telegram_interaction/
  public.py
  module.py
  contracts/
  application/
  domain/
  adapters/
```

## Allowed dependencies

- Telegram-specific adapters owned by the context
- public contracts from other contexts when interaction flow requires them
- platform intake shell delegating into the context facade

## Forbidden dependencies

- reminder domain owning Telegram interaction logic
- worker/runtime owning Telegram business behavior
- deep imports into other contexts’ internals

## Commands owned

- `group_query_reply`

## Routes owned

- Telegram webhook path(s)

## Transitional extraction notes

- current behavior spans Telegram parser/router/webhook modules and the group query reply job
- command ownership is fixed now: `group_query_reply -> telegram_interaction`

