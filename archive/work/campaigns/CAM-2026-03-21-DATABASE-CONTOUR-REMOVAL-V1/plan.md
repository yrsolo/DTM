# CAM-2026-03-21-DATABASE-CONTOUR-REMOVAL-V1

## Goal
- Remove the disconnected retired-database/store-migration contour from active code, tests, and docs.

## Scope
- Delete dead database platform adapters and store-mode plumbing with no live callers.
- Delete disconnected migration helpers and db-migrate job branch.
- Remove active retired-database mentions from docs and instructions.
- Keep historical database-contour references only under `archive/`.

## Out of Scope
- Reworking live object-storage or queue paths.
- Editing archived historical materials.

## Acceptance
- No active code or docs mention the retired database contour outside `archive/`.
- No active config path exposes `STORE_MODE`, `LEGACY_BLOB_WRITE`, or `WRITE_LEGACY_MILESTONES`.
- Verification passes on the remaining active runtime surface.
