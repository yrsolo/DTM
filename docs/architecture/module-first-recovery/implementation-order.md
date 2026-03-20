# Implementation Order

## Canonical sequence

1. Freeze the canon
2. Top path and runtime clarity
3. Break bootstrap gravity
4. Attachments as a real module
5. Publication and cache aftermath
6. Reminders as a real module
7. Snapshot/rendering hard boundary
8. Access API around the primary read-model
9. Telegram freeze and isolate
10. Physical structure cleanup
11. Guardrails and done

## Why this order

- canon first so the rest does not drift
- top path early so the system becomes readable quickly
- bootstrap before deeper extraction so new modules are not pseudo-modules
- attachments and publication early because they anchor the main browser scenario
- reminders stay active priority
- Telegram comes later because it is reserve capability, not the active product center

## Acceptance language

Attachment, cache, snapshot, and access-api waves are incomplete unless the architecture explicitly supports:

`attachments mutation -> platform/runtime invalidation/orchestration -> snapshot projection -> access_api cached delivery`

The wave is done only when that path is obvious in both docs and code reading.
