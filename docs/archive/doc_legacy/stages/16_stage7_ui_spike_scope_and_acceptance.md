# Stage 7 UI Spike Scope And Acceptance

## Purpose
Define a minimal, testable first web UI spike over Stage 7 artifacts without touching production runtime behavior.

## In Scope (Spike-1)
- Read-only data load from `read_model.json` and `fixture_bundle.json`.
- Three core views:
  - timeline sample list,
  - by-designer sample board,
  - task details sample panel.
- Basic filters:
  - designer,
  - status,
  - date range (timeline).
- Compatibility check gate:
  - validate `schema_version`,
  - ensure required top-level fields exist before render.

## Out Of Scope (Spike-1)
- No editing/write-back to Sheets.
- No auth/roles.
- No production deployment pipeline.
- No replacing current Google Sheets visualization.

## Input Artifacts
- `read_model.json`
- `schema_snapshot.json`
- `fixture_bundle.json`
- storage mode:
  - local dev: `artifacts/...`
  - cloud profile: Object Storage keys

## Acceptance Checklist
- [ ] UI can load fixture bundle and render three core views.
- [ ] Schema validation fails-fast on missing required top-level fields.
- [ ] Unknown optional fields do not break rendering.
- [ ] Filter interactions update visible sample data deterministically.
- [ ] Empty sample datasets are rendered without runtime exception.
- [ ] Cloud profile supports artifact fetch from Object Storage key.

## Exit Decision
Spike-1 is accepted when all checklist items pass and findings are captured for Stage 8 implementation backlog.
