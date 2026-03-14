# Active Tasks

- none

## Done

- CAM-2026-03-12-DOC-CODE-REALIGN-V1 P04: verified current attachment upload contour against code, replaced stale attachment skeleton doc with current runtime contract, and updated main doc map
- CAM-2026-03-14-PEOPLE-SNAPSHOT-AND-SECRET-API-V1: expanded people snapshot to full registry, added secret-only `GET /api/v2/people`, preserved reminder compatibility, and kept `frontend_v2` unchanged
- CAM-2026-03-14-PEOPLE-SNAPSHOT-AND-SECRET-API-V1 P02: split people-registry mail fields into `contact_email` and `yandex_email`, and exposed them as `contactEmail` / `yandexEmail` in the secret-only people API
- CAM-2026-03-14-PEOPLE-SNAPSHOT-AND-SECRET-API-V1 P03: added derived `is_active` / `isActive` using safe vacation/termination markers and explicitly kept `.` as active
- CAM-2026-03-14-ARCHITECTURE-AUDIT-AND-ROADMAP-V1: completed code-backed architecture audit, subsystem scorecard, prioritized findings, and multi-wave refactor roadmap for active runtime
- CAM-2026-03-12-DOC-CODE-REALIGN-V1 P03: rewrote current docs around the snapshot-first runtime, removed YDB/readmodel/planner-era stories from active narrative, and archived the snapshot-engine migration plan
- CAM-2026-03-12-DOC-CODE-REALIGN-V1 P02: consolidated auth docs into a canonical contract/runbook set, documented external auth contour ownership, callback routes, Lockbox/env secret wiring, and test/prod verification steps

- Removed false prod config-load guard that blocked same source/target spreadsheet; unsafe render protection now stays only at worksheet-level (`ТАБЛИЧКА`)
- Trigger timer queue fan-out: `timer` trigger now enqueues `update_snapshot`, `render_timeline_sheet`, and `render_designers_sheet` instead of only `update_snapshot`
- CAM-2026-03-12-METRICS-HOTPATH-AND-READ-PERF-V1 P05: disabled `dtm.api.*` and `dtm.info.*` remote writes on hot HTTP read path while preserving `Server-Timing`, in-process traces, and refresh/render/worker metrics
- CAM-2026-03-12-METRICS-HOTPATH-AND-READ-PERF-V1 P04: shipped buffered one-flush-end metrics delivery with `METRICS_DELIVERY_MODE=off|buffered`, restored Monitoring/Prometheus on `test`, and verified direct `/api` stays near fast path
- CAM-2026-03-12-METRICS-HOTPATH-AND-READ-PERF-V1 P03: opened test-only A/B experiment for direct `/api` latency by disabling Prometheus remote-write on the `test` deploy workflow
- CAM-2026-03-12-DIRECT-API-TRUSTWORTHY-DIAGNOSTICS-V1 P01: split direct `/api` latency into `router_precheck_total`, `router_handler_total`, `router_total`, `http_shell_post_router`, and `function_total`
- CAM-2026-03-12-DIRECT-API-TRUSTWORTHY-DIAGNOSTICS-V1 P02: aligned `FrontendV2Handler` totals with router timing ownership, added `query_parse` and `handler_total`, and removed leaked internal timing headers from public `stages` responses
- CAM-2026-03-12-DIRECT-API-TRUSTWORTHY-DIAGNOSTICS-V1 P03: republished `test`, captured live `Server-Timing` and `/info` detail evidence, and localized direct `/api` latency into `inside_handler` and `after_handler` segments
- CAM-2026-03-12-BOTTLENECK-ANALYTICS-V1 P01: added config-gated profiling policy (`off|stages|debug`) with backward compatibility for legacy `dev_mode_metrics`
- CAM-2026-03-12-BOTTLENECK-ANALYTICS-V1 P02: instrumented frontend read path with `dtm.api.stage.*` metrics and recent in-process stage trace recorder
- CAM-2026-03-12-BOTTLENECK-ANALYTICS-V1 P03: exposed bottleneck diagnostics in `/info`, republished Grafana panels, and verified live `api`/`bff` stage traces on `test`
- CAM-2026-03-12-DIRECT-API-OUTER-LATENCY-DECOMPOSITION-V1 P01: instrumented direct `/api` function/shell/dispatch/response boundaries with `dtm.api.outer.*`
- CAM-2026-03-12-DIRECT-API-OUTER-LATENCY-DECOMPOSITION-V1 P02: exposed direct `/api` outer timing through `Server-Timing` and `/info` detail without changing payload contract
- CAM-2026-03-12-DIRECT-API-OUTER-LATENCY-DECOMPOSITION-V1 P03: republished Grafana and verified on `test` that outer contour, not inner frontend stages, dominates direct `/api` latency
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
- latest bottleneck finding: direct `/api` router precheck is negligible and frontend inner core is sub-second, but live latency is dominated by `unexplained_inside_handler` plus `unexplained_after_handler`; the next wave should target those two segments instead of router matching or payload build
