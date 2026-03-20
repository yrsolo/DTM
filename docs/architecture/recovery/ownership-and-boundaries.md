# Ownership And Boundaries

## Ownership rule

Every active scenario must have one obvious owning module.

Examples:
- snapshot refresh and query logic -> `snapshot`
- sheet render flows -> `rendering`
- reminder selection and delivery -> `reminders`
- upload/finalize/preview/delete/read attachment lifecycle -> `attachments`
- Telegram webhook and group-query reply -> `telegram_interaction`
- frontend read surface, masking, cache policy, attachment read access shaping -> `access_api`

Attachment publication scenario:
- `attachments` owns mutation lifecycle and publication readiness
- `platform/runtime` owns invalidation/orchestration after mutation
- `snapshot` owns projection into task card read-side
- `access_api` owns cached browser delivery of the card payload

## Boundary rule

Modules may communicate only through:
- `public.py`
- `contracts`
- explicit commands, queries, or intents

Forbidden:
- deep imports into another module's internals
- direct imports into old technical clusters once the owning wave has migrated them
- using cache helpers as semantic cross-module glue

## Snapshot boundary

Special rule:
- external modules must not rely on `get_snapshot_engine()` long-term
- `snapshot` must evolve toward capability-oriented public APIs
- `rendering` may depend only on snapshot public contracts, never snapshot engine internals

## Cache boundary

Mutating flows must not import frontend HTTP cache helpers directly from jobs or context internals.
All invalidation must go through runtime-owned invalidation intents, jobs, or an access-api-owned invalidation surface.

Special rule for the attachment card scenario:
- `attachments` does not own frontend cache directly
- attachment success is measured by publication into cached task card payload, not by upload/finalize alone
