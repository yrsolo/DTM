# CAM-2026-03-22-HISTORICAL-DOCS-SURFACE-CLEANUP-V1

## Why

Several active docs still carry migration-era material that no longer belongs in the default reading path:
- `docs/architecture/runtime/modularity-audit-2026-03-19.md`
- `docs/architecture/future/*.md`

These files are either historical audits or future skeletons for work that is already implemented or overtaken by the current architecture.

## Goal

Move historical docs out of the active reading path and keep active READMEs focused on the current canon plus explicit archive pointers.

## Trust

- source: current active architecture docs, README links, and runnable code in `src/**`
- last_verified_at: 2026-03-22
- verified_by: Codex
- evidence:
  - direct read of active README link graph
  - direct read of `runtime-canon.md`, `modularity-audit-2026-03-19.md`, and `future/*.md`
  - grep for active references outside archive
- trust_level: high
- notes: these changes are documentation-surface curation only

## Tasks

1. Archive historical runtime/future skeleton docs that no longer belong in the active path.
2. Update active README files and recovery notes to point at current canon or explicit archive locations.
3. Verify active docs no longer reference those archived docs as part of the default reading path.
