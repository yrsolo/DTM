# Evidence - CAM-2026-03-12-DIRECT-API-OUTER-LATENCY-DECOMPOSITION-V1

## Trust gate
- source: active HTTP shell, dispatcher, frontend handler, observability layer
- last_verified_at: 2026-03-12
- verified_by: Codex
- evidence:
  - `src/entrypoints/index_dispatcher.py`
  - `src/entrypoints/http/http_shell.py`
  - `src/entrypoints/http/frontend_v2_handler.py`
  - `src/observability/bottlenecks.py`
- trust_level: high
- notes:
  - `bff` is intentionally out of scope

## Completed Tasks
- [ ] `CAM-2026-03-12-DIRECT-API-OUTER-LATENCY-DECOMPOSITION-V1-P01-T001`
- [ ] `CAM-2026-03-12-DIRECT-API-OUTER-LATENCY-DECOMPOSITION-V1-P01-T002`
- [ ] `CAM-2026-03-12-DIRECT-API-OUTER-LATENCY-DECOMPOSITION-V1-P02-T001`
- [ ] `CAM-2026-03-12-DIRECT-API-OUTER-LATENCY-DECOMPOSITION-V1-P02-T002`
- [ ] `CAM-2026-03-12-DIRECT-API-OUTER-LATENCY-DECOMPOSITION-V1-P03-T001`
- [ ] `CAM-2026-03-12-DIRECT-API-OUTER-LATENCY-DECOMPOSITION-V1-P03-T002`

## Verification
- pending

## Notes
- latest known finding before this campaign: direct `/api` cache-hit inner frontend stages are about `129 ms`, so the dominant unexplained gap is outside the current inner handler path
