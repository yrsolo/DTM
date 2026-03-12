# Active Tasks

- CAM-2026-03-12-METRICS-HOTPATH-AND-READ-PERF-V1 P01: complete evidence for refresh wall-clock, metrics flush overhead, and default read/info latency after local summary/detail split
- CAM-2026-03-12-DOC-CODE-REALIGN-V1 P01: build doc drift matrix against verified runtime code and architecture values
- CAM-2026-03-12-BROWSER-AUTH-AND-MASKED-ACCESS-V1 P00: keep auth wave blocked on Stage 1 and Stage 2 facts; use `agent/intructions/DTM-test/BACKEND_AUTH_HANDOFF.md` as external handoff source

## Done

- CAM-2026-03-12-RUNTIME-DEPLANNERIZE-AND-BOOTSTRAP-HARDENING-V1 P01: removed import-time `AppContext` bootstrap from `index.py` and `src/entrypoints/runtime/planner_runtime_entry.py`; added import-safe smoke coverage
- CAM-2026-03-12-METRICS-HOTPATH-AND-READ-PERF-V1 P01a: split `/info` into default summary and explicit detail mode with `dtm.info.summary.ms` and `dtm.info.detail.ms`

## Notes

- `agent/intructions/DTM-test/**` is reference-only input and must not be used as execution tracking.
- Working plans and evidence must live only in `work/roadmap/campaigns/<CAMPAIGN>/`.
- Telegram/reminder/group-query remains frozen for this wave unless break/fix work is required.
