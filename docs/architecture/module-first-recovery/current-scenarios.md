# Current Scenarios

This document records the product and operational scenarios that should govern the architecture.

## Primary user read scenario

### User gets the main task-list payload
- Actor: site user
- Goal: open the main interface and quickly receive ready-to-render data
- Important: the main payload already contains card data and attachments
- Owning module: `access_api`

### User sees attachment inside the main payload
- Actor: site user
- Goal: see the attachment as part of the normal read-side response
- Important: attachment must already be published into the read-model and not assembled inline
- Owning modules:
  - `access_api` for browser-facing delivery
  - `attachments` for lifecycle and publication readiness
  - `snapshot` for projection into the read-model

## Attachment publication scenario

### Admin uploads attachment quickly
- Actor: admin
- Goal: accept mutation fast without waiting for heavy processing
- Owning module: `attachments`

### Admin waits for publication into the read-model
- Actor: admin
- Goal: know when the attachment is truly visible to users in the main task-list payload
- Important:
  - upload accepted is not enough
  - finalize is not enough
  - preview completion alone is not enough
  - success means publication into the main read-model and appearance in the next normal browser payload
- Owning modules:
  - `attachments` for mutation lifecycle
  - `platform.runtime` for invalidation/orchestration aftermath
  - `snapshot` for projection
  - `access_api` for cached browser delivery

## Reminder scenario

### System sends reminders
- Actor: runtime/scheduler
- Goal: select candidates, build reminder payloads, and deliver them
- Owning module: `reminders`

## Telegram scenario

### Reserve interaction capability
- Actor: Telegram user or runtime webhook
- Goal: keep webhook/group-query interaction available without turning it into the active product center
- Architecture stance: isolate and keep low-maintenance; do not let Telegram reshape the main canon
- Owning module: `telegram_interaction`
