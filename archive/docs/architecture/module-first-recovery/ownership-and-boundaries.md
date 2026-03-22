# Ownership And Boundaries

## Ownership rule

Every active scenario must have one obvious owning module.

Examples:
- snapshot refresh and query logic -> `snapshot`
- sheet rendering -> `rendering`
- reminder selection and delivery -> `reminders`
- upload/finalize/delete/preview lifecycle -> `attachments`
- browser task-list read payload and masking -> `access_api`
- Telegram webhook/group-query reserve flow -> `telegram_interaction`

## Attachment publication ownership

- `attachments` owns mutation lifecycle and publication readiness
- `platform.runtime` owns invalidation/orchestration aftermath
- `snapshot` owns projection into the primary read-model
- `access_api` owns cached browser delivery

## Boundary rule

Modules may communicate only through:
- `public.py`
- `contracts`
- explicit commands, queries, or intents

Forbidden:
- deep imports into another module's internals
- reintroducing historical technical clusters as real architecture centers
- using cache helpers as semantic glue

## Special stance on Telegram

`telegram_interaction` stays available, but:
- is not allowed to drive the main architecture roadmap
- must not force deep reminder redesign
- should be kept isolated and low-maintenance unless product priority changes
