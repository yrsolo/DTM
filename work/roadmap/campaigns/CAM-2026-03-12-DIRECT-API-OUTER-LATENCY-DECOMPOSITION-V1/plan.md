# CAM-2026-03-12-DIRECT-API-OUTER-LATENCY-DECOMPOSITION-V1 Plan

## Phases

### P01 - Direct API outer timing
- `CAM-2026-03-12-DIRECT-API-OUTER-LATENCY-DECOMPOSITION-V1-P01-T001` instrument direct `/api` request build, router dispatch, response build, shell total, and function total
- `CAM-2026-03-12-DIRECT-API-OUTER-LATENCY-DECOMPOSITION-V1-P01-T002` link outer trace with existing frontend inner trace

### P02 - Debug surfaces
- `CAM-2026-03-12-DIRECT-API-OUTER-LATENCY-DECOMPOSITION-V1-P02-T001` add `Server-Timing` and minimal debug headers for direct `/api` in `stages/debug`
- `CAM-2026-03-12-DIRECT-API-OUTER-LATENCY-DECOMPOSITION-V1-P02-T002` expose recent direct `/api` outer traces in `/info` detail

### P03 - Evidence and dashboard
- `CAM-2026-03-12-DIRECT-API-OUTER-LATENCY-DECOMPOSITION-V1-P03-T001` add Grafana panels for direct `/api` outer vs inner timings
- `CAM-2026-03-12-DIRECT-API-OUTER-LATENCY-DECOMPOSITION-V1-P03-T002` deploy to `test` and capture live direct `/api` evidence
