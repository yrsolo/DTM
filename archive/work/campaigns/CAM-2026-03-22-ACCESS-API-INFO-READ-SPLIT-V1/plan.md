# CAM-2026-03-22-ACCESS-API-INFO-READ-SPLIT-V1 Plan

## Trust Gate
- source: `src/contexts/access_api/internal/operational_info_read_api.py`, `src/contexts/access_api/application/browser_read_api.py`, `tests/contexts/access_api/test_info_observability.py`, `tests/contexts/access_api/test_frontend_api_routing.py`
- last_verified_at: 2026-03-22
- verified_by: Codex
- evidence:
  - `Get-ChildItem src/contexts -Recurse -Filter *.py | Sort-Object Length -Descending | Select-Object -First 20 FullName,Length`
  - `rg -n "OperationalInfoReadApi|_storage_stats|/info|info_observability" tests src`
  - direct reads of `operational_info_read_api.py` and the active tests that monkeypatch its storage seam
- trust_level: high
- notes:
  - `OperationalInfoReadApi` was still a giant mixed adapter/service file; the live tests only depended on its `_storage_stats` seam and `handle()` surface, so the internal orchestration could move safely into an application-owned service.

## Phases

### P01 - Split The Giant Info Reader
- `CAM-2026-03-22-ACCESS-API-INFO-READ-SPLIT-V1-P01-T001` Introduce an application-owned operational info read service and move summary/detail payload orchestration into it.
- `CAM-2026-03-22-ACCESS-API-INFO-READ-SPLIT-V1-P01-T002` Keep `OperationalInfoReadApi` as a thin HTTP adapter that preserves the `_storage_stats` test seam and delegates to the new service.

### P02 - Verification And Tracking
- `CAM-2026-03-22-ACCESS-API-INFO-READ-SPLIT-V1-P02-T001` Run the targeted info/read-routing/guardrail/import-safety contour.
- `CAM-2026-03-22-ACCESS-API-INFO-READ-SPLIT-V1-P02-T002` Close out tracking and archive the completed campaign record.
