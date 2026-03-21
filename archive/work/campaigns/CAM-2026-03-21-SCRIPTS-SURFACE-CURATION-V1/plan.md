# CAM-2026-03-21-SCRIPTS-SURFACE-CURATION-V1

## Goal
- Curate the active `scripts/` surface so it contains only live operator and CI helpers.

## Scope
- Archive disconnected helper scripts that no longer participate in active runtime, CI, or operator flows.
- Refresh live guard scripts so they point at the current repo contour instead of removed roots.
- Update tracking with trust/evidence from code and workflow verification.

## Out of Scope
- Reworking live observability provisioning scripts.
- Changing deploy workflow behavior.

## Acceptance
- `scripts/` contains only live guardrails or active operator commands.
- Archived scripts remain available under `archive/work/`.
- Live guard scripts read the current repo map without stale removed-root scopes.
