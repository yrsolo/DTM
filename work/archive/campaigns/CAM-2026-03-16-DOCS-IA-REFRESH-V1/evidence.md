# Evidence - CAM-2026-03-16-DOCS-IA-REFRESH-V1

## Trust gate
- source: current repo `README.md`, active `docs/*` tree, current archive tree
- last_verified_at: 2026-03-16
- verified_by: Codex
- evidence:
  - `README.md`
  - `docs/README.md`
  - active docs moved into `docs/product/*`, `docs/architecture/*`, `docs/integrations/*`, `docs/operations/*`, `docs/reference/*`
  - archive folders indexed with `README.md`
- trust_level: high
- notes:
  - previous active navigation was split across `docs/system/*` and `docs/snapshot_engine/*`
  - multiple active docs still used absolute filesystem links before this wave

## Delivery evidence
- Root `README.md` rewritten as a product-first landing page with relative links into documentation layers.
- `docs/README.md` rewritten as the main documentation map in Russian.
- Active docs were regrouped by reader intent:
  - `docs/product/*`
  - `docs/architecture/*`
  - `docs/integrations/*`
  - `docs/operations/*`
  - `docs/reference/*`
- Each folder in `docs/` now contains a `README.md`.
- Archive folders now have simple local indexes so historical materials are discoverable without scanning raw filenames.
- Relative link normalization check passed across `README.md`, `docs/**/*.md`, and `work/**/*.md`.

## Outcome
- Docs now support two-level onboarding:
  - quick Russian overview layer
  - deeper technical documents by topic
- Old active docs buckets `docs/system/` and `docs/snapshot_engine/` were retired from the active information architecture.
