# Active Tasks

- CAM-2026-03-12-BROWSER-AUTH-AND-MASKED-ACCESS-V1 P01: redeploy backend test contour with Lockbox-mapped `BROWSER_AUTH_PROXY_SECRET` and re-run live full-mode verification

## Done

- CAM-2026-03-12-RUNTIME-DEPLANNERIZE-AND-BOOTSTRAP-HARDENING-V1 P01: removed import-time `AppContext` bootstrap from `index.py` and `src/entrypoints/runtime/planner_runtime_entry.py`; added import-safe smoke coverage
- CAM-2026-03-12-METRICS-HOTPATH-AND-READ-PERF-V1 P01a: split `/info` into default summary and explicit detail mode with `dtm.info.summary.ms` and `dtm.info.detail.ms`
- CAM-2026-03-12-METRICS-HOTPATH-AND-READ-PERF-V1 P01: owner accepted current Stage 2 evidence as sufficient to open Stage 4
- CAM-2026-03-12-DOC-CODE-REALIGN-V1 P01: rebuilt active main docs around verified Stage 1/2 runtime facts, canonical architecture values, and compact Grafana/info observability story

## Notes

- `agent/intructions/DTM-test/**` is reference-only input and must not be used as execution tracking.
- Working plans and evidence must live only in `work/roadmap/campaigns/<CAMPAIGN>/`.
- Telegram/reminder/group-query remains frozen for this wave unless break/fix work is required.
