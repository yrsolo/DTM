# CAM-LEGACY-CUT-API-V1.evidence

## Trust gate
- source: `src/snapshot_engine/query_engine.py`, `src/snapshot_engine/frontend_v2_payload_builder.py`, `tests/snapshot_engine/test_query_engine.py`, `tests/api/test_frontend_api_routing.py`
- last_verified_at: 2026-03-06
- verified_by: Codex agent
- trust_level: high
- evidence:
  - direct code scan showed legacy deps in snapshot query path (`core.api_payload_v2`, `core.models.people.Person`, `pandas`).
  - after refactor those imports were removed from query path.

## Execution evidence
- implemented `FrontendV2PayloadBuilder` in snapshot engine.
- switched `SnapshotQueryEngine` to builder-based payload generation.
- preserved fields `status` + `history` in tasks payload.

## Verification
- `python -m unittest tests.snapshot_engine.test_query_engine -v` -> OK
- `python -m unittest tests.api.test_frontend_api_routing -v` -> OK
- `python scripts/check_no_legacy_imports.py` -> OK for targeted contours.

## Notes
- legacy remains in other runtime contours (planner/group query legacy helper path) and is tracked in later campaigns.
