# CAM-LEGACY-CUT-API-V1

## Goal
Move API v2 payload building fully to Snapshot Engine without legacy builder dependencies.

## Scope
- Replace legacy `core/api_payload_v2` usage in snapshot query path.
- Keep API v2 contract parity (`status`, `history`, filters, window, limit, include_people).
- Remove pandas/person model coupling from snapshot API build path.

## Phases and Tasks
### P01 - Parity spec
- P01-T001: Freeze current API v2 parity spec (fields, filters, semantics).
- P01-T002: Add `docs/snapshot_engine/api_v2_parity.md`.

### P02 - New builder
- P02-T001: Add `src/snapshot_engine/frontend_v2_payload_builder.py` skeleton.
- P02-T002: Implement tasks serialization (`status`, `history`, dates, milestones).
- P02-T003: Implement entities/enums from PrepSnapshot.

### P03 - Query engine wiring
- P03-T001: Inject builder into `SnapshotQueryEngine` constructor.
- P03-T002: Remove legacy builder imports from snapshot engine modules.

### P04 - Tests
- P04-T001: Unit parity tests for statuses/window/limit/include_people/history.
- P04-T002: Golden payload test from fixed PrepSnapshot fixture.

### P05 - Guards
- P05-T001: Grep gate for `core.api_payload_v2`, `pandas`, `core.models.people` in `src/snapshot_engine`.

## DoD
- API v2 runtime path does not import legacy payload builder/pandas/core person models.
- Payload contract parity preserved.
