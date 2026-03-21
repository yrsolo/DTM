# CAM-2026-03-21-TESTS-ROOT-REALIGNMENT-V1

## Goal
- Move still-live tests out of the stale `tests/services` shelf into role-true active homes.

## Scope
- Rehome `tests/services/*` into `tests/contexts`, `tests/entrypoints`, `tests/platform`, and `tests/agent`.
- Remove the old `tests/services` root once empty.
- Verify the moved tests under their new module-first homes.

## Acceptance
- `tests/services` no longer exists as an active top-level test root.
- Moved tests live under role-true homes.
- Targeted verification passes on the new import paths.
