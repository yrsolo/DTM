# Evidence

## Freshness And Trust

- source: owner request in current chat
  - last_verified_at: 2026-06-15
  - verified_by: Codex
  - evidence: Requested a shorter ShadowGen-style light page with tabs for video, screen, back, front, notification and technically accurate hybrid diagrams.
  - trust_level: high
  - notes: Direct current owner instruction.
- source: ShadowGen public reference
  - last_verified_at: 2026-06-15
  - verified_by: Codex
  - evidence: `https://yrsolo.github.io/ShadowGen-ML-service/` returned HTTP 200 and will be used as visual/layout reference.
  - trust_level: high
  - notes: Public runnable reference page.
- source: current DTM showcase repo surface
  - last_verified_at: 2026-06-15
  - verified_by: Codex
  - evidence: `git status --short --branch` showed clean `dev...origin/dev`; existing site files live under `site/`.
  - trust_level: high
  - notes: Static GitHub Pages surface; no backend runtime changes needed.

## Local Verification

- source: static asset references
  - last_verified_at: 2026-06-15
  - verified_by: Codex
  - evidence: Parsed `site/index.html` local `src`/`href`/`poster` references; 7 local references found, 0 missing. Parsed `screen-workspace.svg`, `backend-flow-light.svg`, `frontend-flow-light.svg`, `notification-flow-light.svg`, and `favicon.svg` as XML successfully.
  - trust_level: high
  - notes: Static file graph is internally consistent.
- source: local Pages smoke
  - last_verified_at: 2026-06-15
  - verified_by: Codex
  - evidence: Local server returned HTTP 200 for `/`, `/#video`, `/#screen`, `/#back`, `/#front`, and `/#notification`. Promo HLS manifest and HLS.js CDN returned HTTP 200.
  - trust_level: high
  - notes: Desktop and mobile screenshots were rendered with headless Edge; mobile hero wrapping was adjusted after visual review.
