# CAM-2026-03-22-PYCACHE-SURFACE-CLEANUP-V1 - Evidence

## Trust Gate

- source: filesystem state
- last_verified_at: 2026-03-22
- verified_by: Codex
- evidence:
  - recursive listing of `__pycache__` directories
- trust_level: high
- notes: generated caches outside `.venv` are removable hygiene artifacts

## Execution Notes

- started: 2026-03-22
- completed: 2026-03-22
- scope: filesystem hygiene only
- removed:
  - 73 repo-local `__pycache__` directories outside `.venv`
- verification:
  - recursive post-clean check for `__pycache__` outside `.venv`
  - root directory listing
  - `tests/` top-level listing
- result:
  - no repo-local `__pycache__` directories remain outside `.venv`
  - root and `tests/` surfaces now read source-only again
