# Implementation Order

## Canonical sequence

1. Freeze the canon
2. Simplify the top path
3. Break bootstrap gravity
4. Attachments as a true first-class module
5. Decouple cache through intents
6. Reminders as a real module
7. Snapshot and rendering split
8. Telegram interaction as a real module
9. Access API as a real module
10. Final structure and archive
11. Guardrails and done

## Why this order

- canon first, so later waves do not drift
- top path next, so the system becomes readable quickly
- bootstrap before deeper extraction, so new modules do not remain pseudo-modules
- attachments first because it is the strongest extraction candidate
- cache decoupling early because cache is currently one of the main cross-module glue points
- snapshot/rendering later because it is the riskiest boundary and should be cut after module discipline is stronger

## Scenario acceptance language

Attachment, cache, snapshot, and access-api waves are not complete unless the architecture clearly supports this path:

`attachments mutation -> platform/runtime invalidation/orchestration -> snapshot projection -> access_api cached delivery`

For this scenario:
- upload and `finalize` are only mutation-start signals
- terminal job success is not enough by itself
- the wave is complete only when attachment publication into the cached task card payload is an explicit supported path in the docs and architecture
