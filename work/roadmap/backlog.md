# Backlog

## In Progress
- CAM-UNIFIED-API-INGRESS-V1
- CAM-GRAFANA-PROM-OPS-DASHBOARD-V1
- CAM-SHEETS-PERF-STATS-AND-YDB-ENV-CUT-V1

## Planned
- none

## Done
- CAM-SNAPSHOT-PREP-BULK-REFORM-V1
- CAM-2026-03-10-DATALENS-OPS-DASHBOARD-V1 (repo/DataLens foundation complete; API chart provisioning blocked externally)
- CAM-SNAPSHOT-RENDER-TIMINGS-V1
- CAM-2026-03-09-YC-MONITORING-INTEGRATION-V1
- CAM-2026-03-09-TELEGRAM-COMMAND-ROUTER-V1
- CAM-2026-03-09-OBSERVABILITY-FOUNDATION-V1
- CAM-2026-03-09-GREP-GATES-V1
- CAM-2026-03-09-QUEUE-RETRY-SEMANTICS-V1
- CAM-LEGACY-ARCHIVE-CLEANUP-V1
- CAM-ENTRYPOINT-LEGACY-CUT-FINAL-V1
- CAM-INFO-OPS-OBSERVABILITY-V1
- CAM-FILE-ATTACHMENTS-V1
- CAM-TELEGRAM-INTAKE-V1
- CAM-GROUP-QUERY-UNIFY-WITH-REMINDER-V1
- CAM-ADMIN-ACTIONS-ASYNC-V1
- CAM-QUEUE-FOUNDATION-ON-CF-V1

## Parked
- CAM-2026-03-09-RUNTIME-DEPLANNERIZE-V1 (obsolete / already substantially delivered)

## Notes
- Queue retry semantics, grep gates, observability foundation, and Telegram command router are now treated as completed hardening slices on top of the already delivered post-legacy baseline.
- `/info` remains the operator dashboard and job-status store remains the source of truth for recent command execution state.
- YC Monitoring integration is complete for the selected test-first scope: test contour emits real custom metrics and the test dashboard exists.
- Current active hardening slice adds operation-level timing visibility for snapshot update and render.
- Current DataLens ops-dashboard slice is partially delivered and now parked as an external platform blocker: repo support, workbook, and Monitoring connection are created; chart/dashboard automation is blocked by live DataLens API `createQLChart` failures against the Monitoring connection.
- The folder-access hypothesis for DataLens has been tested and exhausted: the real API caller now has folder `viewer` and `monitoring.viewer`, but `createQLChart` still fails with the same backend error.
- Current active dashboard path is Grafana-over-Prometheus: repo-side dual-write/Grafana foundation now includes a real Yandex Managed Prometheus remote-write client; shared workspace `mon73oiiclfbmmqbjejn`, Grafana datasource, and public dashboard are now in place, and the remaining rollout work is limited to server-side `allow_embedding = true` plus broader live sample coverage on `test`.
- Snapshot prep bulk reform is complete on `test`: hard-switch runtime is live, migration on `test` was a no-op, and observed `build_prep_ms` dropped from about `12117 ms` to about `58.86 ms`.
- Separate follow-ups remain outside this CAM:
  - `/info` build metadata 404 in `yc_function_info.py`
  - notify enqueue path inconsistency on test
