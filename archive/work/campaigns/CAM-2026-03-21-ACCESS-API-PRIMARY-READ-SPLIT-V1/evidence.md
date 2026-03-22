# Evidence - CAM-2026-03-21-ACCESS-API-PRIMARY-READ-SPLIT-V1

## Trust gate
- source: current `PrimaryTaskListReadApi`, current `access_api` module/application surface, current tests, owner critique
- last_verified_at: 2026-03-21
- verified_by: Codex
- evidence:
  - `agent/owner_inputs/crit.md`
  - `src/contexts/access_api/internal/primary_task_list_read_api.py`
  - `src/contexts/access_api/application/browser_read_api.py`
  - `tests/contexts/access_api/test_frontend_api_routing.py`
  - `tests/contexts/access_api/test_frontend_api_v2_payload.py`
- trust_level: high
- notes:
  - critique is already integrated into active tracking; this wave narrows one concrete seam from that critique

## Result
- `PrimaryTaskListReadApi` is now a thin HTTP adapter responsible only for route matching, doc responses, and delegating the data path
- `PrimaryTaskListReadService` owns the primary browser read orchestration as an application service
- compatibility seams for snapshot query, prep snapshot, response cache store, and frontend query execution were preserved via explicit dependency injection so active behavior and tests stayed unchanged

## Verification
- `python -m unittest tests.contexts.access_api.test_frontend_api_routing tests.contexts.access_api.test_frontend_api_v2_payload tests.contexts.access_api.test_info_observability tests.contexts.access_api.test_task_attachment_read_api tests.architecture.test_guardrails_v0 tests.entrypoints.test_import_safety -v`
- Result: `89 tests`, `OK`
