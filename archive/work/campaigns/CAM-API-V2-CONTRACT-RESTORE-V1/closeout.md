# CAM-API-V2-CONTRACT-RESTORE-V1 Closeout

## Result
- Restored `brand`, `format_`, `customer` in API v2 `tasks[]` payload.
- Restored default people emission for readmodel-built payload (`include_people=true`, people derived from owner rows).
- Added practical query examples to API v2 docs (JSON + HTML).

## Verification
- Targeted smoke/tests are green (35 tests in selected contour).

## Notes
- Root cause of missing people: readmodel builder persisted snapshots with `include_people=False` and empty people list.
