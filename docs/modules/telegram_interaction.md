# Telegram Interaction

## Purpose

`telegram_interaction` owns:
- Telegram webhook intake
- Telegram update parsing
- update-to-command mapping
- Telegram interaction flows for group/user replies

Current architecture stance:
- keep this module available and isolated
- keep it low-maintenance unless product priority changes
- do not let it reshape the main read-side or reminder roadmap
- preserve reserve capability contour instead of polishing for ideal architecture

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

## Minimal reserve contour

The following behavior must keep working:
- webhook intake
- update parsing and routing needed for current interaction flows
- `group_query_reply`
- reminder delivery channel through Telegram where already used

## Transitional extraction notes

- current behavior spans Telegram parser/router/webhook modules and the group query reply job
- command ownership is fixed now: `group_query_reply -> telegram_interaction`
- this module is a reserve capability, not a co-equal active architecture priority with the primary browser read-side
