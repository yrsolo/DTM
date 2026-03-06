# CAM-HTTP-FALLBACK-REMOVAL-V1.evidence

## Trust gate
- source: `src/entrypoints/http/frontend_v2_handler.py`, `src/snapshot_engine/query_engine.py`, `tests/api/test_frontend_api_routing.py`
- last_verified_at: 2026-03-06
- verified_by: Codex agent
- trust_level: high
- evidence:
  - handler path reads only via `build_snapshot_engine(...).frontend_v2(...)`.
  - legacy fallback builder/import branches absent in runtime path.

## Execution evidence
- confirmed removal of legacy HTTP fallback in API v2 handler path.
- standardized unavailable response to:
  - `status=503`
  - `error.code=frontend_source_unavailable`
  - `error.details.source=snapshot`

## Verification
- `python -m unittest tests.api.test_frontend_api_routing -v` -> OK
- `python scripts/check_no_legacy_imports.py` -> OK

