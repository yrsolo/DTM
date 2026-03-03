# Stage 7 Shadow-Run Readiness Checklist

## Goal
Confirm a visualization data consumer can run in shadow mode over Stage 7 artifacts without affecting production flow.

## Preconditions
- `read_model.json`, `schema_snapshot.json`, `fixture_bundle.json` are produced for the same run.
- Storage mode is defined:
  - local dev: filesystem artifacts
  - cloud profile: Object Storage keys

## Checklist
- [ ] Consumer reads artifacts in read-only mode.
- [ ] Consumer validates `schema_version` and required top-level fields.
- [ ] Consumer logs clear diagnostic on schema mismatch without hard crash loop.
- [ ] Consumer handles unknown optional fields as non-fatal.
- [ ] Consumer renders empty states for empty datasets.
- [ ] No write-back calls to Sheets/production endpoints in shadow mode.
- [ ] Shadow run captures basic metrics: load time, render success, schema validation result.
- [ ] Cloud profile fetch works from Object Storage key paths.

## Entry/Exit Rules
- Entry:
  - Stage 7 artifacts exist and pass basic smoke checks.
  - UI spike scope (`doc/16`) is accepted.
- Exit:
  - All checklist items pass at least once on local artifacts.
  - Cloud fetch path validated with Object Storage keys.
  - Issues are logged as explicit Stage 8 backlog items.
