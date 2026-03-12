# CAM-SNAPSHOT-RENDER-TIMINGS-V1

## Goal

Expose operation-level timing breakdown for the two heaviest user-visible pipelines:

- snapshot update
- render

## Scope

- instrument snapshot update with:
  - `dtm.snapshot.fetch_sheet_ms`
  - `dtm.snapshot.normalize_ms`
  - `dtm.snapshot.build_prep_ms`
  - `dtm.snapshot.write_raw_ms`
  - `dtm.snapshot.write_prep_ms`
  - existing `dtm.snapshot.update_duration_ms`
- instrument render with:
  - `dtm.render.build_plan_ms`
  - `dtm.render.write_sheet_ms`
  - existing `dtm.render.duration_ms`
- return timing breakdown in job result payloads
- keep existing public API contracts additive only

## Non-goals

- no redesign of render/snapshot logic
- no `/info` redesign
- no metrics backend changes

## DoD

- snapshot update emits and returns detailed timings
- render timeline/designers emit and return detailed timings
- tests cover timing fields without breaking current behavior
- docs/tracking reflect the new metric visibility
