# Backlog

## In Progress
- CAM-2026-03-09-YC-MONITORING-INTEGRATION-V1

## Planned
- none

## Done
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
- YC Monitoring integration is in the rollout stage: code, config, and test dashboard are ready; remaining work is deployed test smoke on the live function.
