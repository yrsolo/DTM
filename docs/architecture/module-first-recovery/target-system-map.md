# Target System Map

## Main reading shape

The active code map should read as:
- `entrypoint`
- `platform.runtime`
- owning modules

Nothing else should compete with that picture.

## Active owning modules

- `snapshot`
- `rendering`
- `reminders`
- `attachments`
- `access_api`

## Reserve module

- `telegram_interaction`

It stays alive, isolated, and usable, but is not a co-equal active architecture priority.

## Platform layer

- `platform.runtime`

Owns:
- mode classification
- queue dispatch
- trigger orchestration
- runtime diagnostics
- publication aftermath and invalidation coordination

Does not own:
- snapshot logic
- attachment lifecycle
- reminder business rules
- rendering rules
- browser response shaping

## Non-owning historical zones

The following must not return as architecture centers:
- generic `jobs` as the way to understand behavior
- generic `services`
- historical clusters like old `render`, `notify`, `telegram`
- HTTP handlers as ownership centers
- broad engine-shaped access surfaces
