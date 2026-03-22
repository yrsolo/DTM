# CAM-2026-03-22-PYCACHE-SURFACE-CLEANUP-V1

## Why

Active repo surface still contains generated `__pycache__` directories in root, `src`, `tests`, `agent`, and other tracked homes.

## Goal

Remove all repo-local `__pycache__` directories outside `.venv` so the visible repo surface stays source-only.

## Trust

- source: filesystem state
- last_verified_at: 2026-03-22
- verified_by: Codex
- evidence:
  - recursive directory listing for `__pycache__`
- trust_level: high
- notes: generated caches are never canonical project state

## Tasks

1. Delete all `__pycache__` directories outside `.venv`.
2. Verify no such directories remain in the active repo surface.
