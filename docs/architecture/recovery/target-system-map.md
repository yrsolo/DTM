# Target System Map

## Primary reading shape

The project must read as:

- `src/entrypoint`
- `src/platform/runtime`
- owning modules in `src/contexts`

No technical cluster should compete with this map as an architectural center.

## Owning modules

- `snapshot`
- `rendering`
- `reminders`
- `attachments`
- `telegram_interaction`
- `access_api`

## Platform runtime

`platform.runtime` owns only:
- runtime classification
- worker command dispatch
- trigger orchestration
- runtime diagnostics
- health and ops surfaces
- cache invalidation orchestration if cache invalidation is runtime-owned

## Demoted technical clusters

These roots are not acceptable as first-class architecture centers:
- `src/jobs`
- `src/services`
- `src/render`
- `src/notify`
- `src/telegram`
- `src/entrypoints/http`
- `src/snapshot_engine`

They may exist temporarily as implementation zones only while they are being moved under owning modules or explicitly demoted.
