# Frontend API Changelog

## Versions

### v1 (current legacy-compatible)
- Endpoints:
  - `GET /api/v1/frontend`
  - `GET /api/v1/read-model` (alias)
  - `GET /api/v1/frontend/doc`
- Contract is legacy-flat and kept stable for existing consumers.

### v2 (new)
- Endpoints:
  - `GET /api/v2/frontend`
  - `GET /api/v2/frontend/doc`
- Contract is normalized and extensible:
  - `meta + filters + summary + entities + tasks`

## Compatibility Rules
1. v1 remains unchanged while v2 is introduced in parallel (Strangler Pattern).
2. New fields in v2 are additive/optional by default.
3. Breaking changes are introduced only in a new major version (`v3`).
4. `task.hash` and `task.revision` are reserved fields in v2; may be `null` until full versioning rollout.

## Rollout Policy
- Existing clients stay on v1.
- New clients should integrate v2.
- Future generic alias `/api/frontend` may use `FRONTEND_API_DEFAULT_VERSION` (`v1|v2`), but explicit versioned routes remain authoritative.
