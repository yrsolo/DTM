# CAM-2026-03-16-DOCS-IA-REFRESH-V1

## Summary

Refresh the repository documentation information architecture so new readers can enter from a simple Russian overview layer and then drill into deeper technical docs through relative links.

## Planned work

1. Replace the old active `docs/system/*` and `docs/snapshot_engine/*` navigation model with reader-intent folders.
2. Rewrite the repo root `README.md` as a product-first landing page.
3. Add `README.md` to every directory under `docs/`.
4. Normalize repo-internal links to relative Markdown paths.
5. Add lightweight archive indexes so historical folders are navigable.

## Acceptance

- Every folder under `docs/` has a `README.md`.
- Active docs are grouped under `product/`, `architecture/`, `integrations/`, `operations/`, and `reference/`.
- Root `README.md` is product-first and links to deeper docs.
- A repo-wide markdown grep for absolute internal link patterns returns no matches.
