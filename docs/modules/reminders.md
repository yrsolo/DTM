# Reminders

## Purpose

`reminders` owns reminder business logic:
- candidate selection
- reminder payload building
- styling/enhancement
- delivery orchestration
- retry/accounting behavior that belongs to reminder execution

## Public facade expectation

Target context shape:

```text
src/contexts/reminders/
  public.py
  module.py
  contracts/
  application/
  domain/
  adapters/
```

## Allowed dependencies

- delivery adapters owned by the context
- optional LLM styling adapter owned by the context
- public contracts from other contexts if reminder flow needs prepared state

## Forbidden dependencies

- treating `morning` trigger semantics as the reminder domain itself
- deep imports into Telegram internals or runtime transport internals
- business rules inside trigger shells

## Commands owned

- `send_reminders`

## Routes owned

- no primary HTTP routes are expected as the main ownership center in this wave
- trigger intake remains platform-owned; reminder execution ownership remains here

## Active implementation notes

- reminders remain an active operational priority
- keep behavior stable while separating reminder logic from trigger semantics and transport details
- reminders must not depend on deep Telegram redesign; Telegram is reserve capability, reminders are active product/runtime flow
- Telegram support for reminders should be maintained as an existing delivery channel, not as a reason to re-center the architecture on Telegram
