# CAM-2026-03-21-TESTS-SURFACE-CURATION-V1

## Goal
- Remove empty and disconnected historical shelves from the top-level `tests/` surface.

## Scope
- Delete empty legacy test roots and stale placeholder files.
- Clear repo test `__pycache__` leftovers.
- Keep all live test homes (`architecture`, `api`, `contexts`, `core`, `entrypoints`, `platform`, etc.) intact.

## Out of Scope
- Reorganizing still-populated test roots such as `tests/services` or `tests/api`.
- Moving live test files between active homes.

## Acceptance
- Empty historical test roots no longer appear in the top-level `tests/` map.
- `tests/handlers/__init__.py` no longer survives as an orphan placeholder.
- Verification suite still passes.
