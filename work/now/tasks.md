# Active Tasks

- CAM-2026-03-12-DIRECT-API-OUTER-LATENCY-DECOMPOSITION-V1 P01: instrument direct `/api` outer timing at function/shell/dispatch/response boundaries
- CAM-2026-03-12-DIRECT-API-OUTER-LATENCY-DECOMPOSITION-V1 P02: expose direct `/api` debug timing through `Server-Timing` headers and `/info` detail
- CAM-2026-03-12-DIRECT-API-OUTER-LATENCY-DECOMPOSITION-V1 P03: republish Grafana and capture live `test` evidence for direct `/api`

## Done

- CAM-2026-03-12-BOTTLENECK-ANALYTICS-V1 P01: added config-gated profiling policy (`off|stages|debug`) with backward compatibility for legacy `dev_mode_metrics`
- CAM-2026-03-12-BOTTLENECK-ANALYTICS-V1 P02: instrumented frontend read path with `dtm.api.stage.*` metrics and recent in-process stage trace recorder
- CAM-2026-03-12-BOTTLENECK-ANALYTICS-V1 P03: exposed bottleneck diagnostics in `/info`, republished Grafana panels, and verified live `api`/`bff` stage traces on `test`
- CAM-2026-03-12-RUNTIME-DEPLANNERIZE-AND-BOOTSTRAP-HARDENING-V1 P01: removed import-time `AppContext` bootstrap from `index.py` and `src/entrypoints/runtime/planner_runtime_entry.py`; added import-safe smoke coverage
- CAM-2026-03-12-METRICS-HOTPATH-AND-READ-PERF-V1 P01a: split `/info` into default summary and explicit detail mode with `dtm.info.summary.ms` and `dtm.info.detail.ms`
- CAM-2026-03-12-METRICS-HOTPATH-AND-READ-PERF-V1 P01: owner accepted current Stage 2 evidence as sufficient to open Stage 4
- CAM-2026-03-12-METRICS-HOTPATH-AND-READ-PERF-V1 P02: default frontend response cache is live for exact `limit=60` all-status query in Object Storage; repeated `api` and `bff` hits on `test` contour are faster, and masked mapping now rotates by Moscow hour
- CAM-2026-03-12-DOC-CODE-REALIGN-V1 P01: rebuilt active main docs around verified Stage 1/2 runtime facts, canonical architecture values, and compact Grafana/info observability story
- CAM-2026-03-12-BROWSER-AUTH-AND-MASKED-ACCESS-V1 P01: backend test contour now maps `BROWSER_AUTH_PROXY_SECRET` from Lockbox; live `masked` and trusted `full` paths verified on `test`

## Notes

- `agent/intructions/DTM-test/**` is reference-only input and must not be used as execution tracking.
- Working plans and evidence must live only in `work/roadmap/campaigns/<CAMPAIGN>/`.
- Telegram/reminder/group-query remains frozen for this wave unless break/fix work is required.
- latest bottleneck finding: cache-hit backend tracked stages are ~`129-132 ms`; remaining `12-14 s` user-visible latency sits outside current backend stage work and should be tackled as a separate infra/runtime optimization wave
