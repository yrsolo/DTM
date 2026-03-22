# CAM-2026-03-22-DOCS-CANON-REBUILD-V1

## Goal
Radically compact active documentation so `docs/` reads as the current system canon rather than a layered migration archive.

## Steps
1. Inventory active docs and decide keep/merge/archive for each cluster.
2. Rebuild active docs around `product / architecture / modules / operations / reference`.
3. Archive old `integrations` and recovery-era architecture trees.
4. Rewrite root/docs navigation around the current system.
5. Update active tracking and references so no primary reading path points into archived docs.

## Acceptance
- `docs/` contains only active system documentation.
- root `README.md` and `docs/README.md` are reader-first and Russian-first.
- active docs no longer depend on `integrations/` or recovery-era architecture roots.
- historical material remains available under `archive/docs/`.
