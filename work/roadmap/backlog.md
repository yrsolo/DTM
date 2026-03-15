# Backlog

## In Progress
- none

## Blocked
- CAM-2026-03-15-TASK-ATTACHMENTS-LIVE-SMOKE-V1

## Planned
- CAM-2026-03-15-TASK-ATTACHMENTS-ORPHAN-CLEANUP-V1

## Done
- Morning reminders skip weekend delivery and preserve Friday -> Monday next-workday behavior
- Attachment post-mutation cache invalidation for exact default frontend response cache after attach/delete
- CAM-2026-03-15-TASK-ATTACHMENTS-ORPHAN-CLEANUP-V1 hidden cleanup enqueue path, job, TTL policy, and tests
- CAM-2026-03-12-DOC-CODE-REALIGN-V1 P04 current attachment-upload doc refresh and skeleton removal
- CAM-2026-03-14-PEOPLE-SNAPSHOT-AND-SECRET-API-V1
- CAM-2026-03-14-TASK-ATTACHMENTS-V1
- CAM-2026-03-14-ARCHITECTURE-AUDIT-AND-ROADMAP-V1
- CAM-2026-03-12-DOC-CODE-REALIGN-V1 P03 current-doc cleanup for legacy/YDB removal and archival pointers
- CAM-2026-03-12-DOC-CODE-REALIGN-V1 P02 auth docs realignment and operator/deploy consolidation
- Remove false prod render-contour config guard at config-load stage
- Trigger timer queue fan-out to snapshot refresh + both render jobs
- CAM-2026-03-12-METRICS-HOTPATH-AND-READ-PERF-V1 P05 hot-read API metrics suppression with live verification on `test`
- CAM-2026-03-12-METRICS-HOTPATH-AND-READ-PERF-V1 P04 buffered metrics delivery redesign and live verification on `test`
- CAM-2026-03-12-DIRECT-API-TRUSTWORTHY-DIAGNOSTICS-V1
- CAM-2026-03-12-DIRECT-API-OUTER-LATENCY-DECOMPOSITION-V1
- CAM-2026-03-12-BOTTLENECK-ANALYTICS-V1
- CAM-2026-03-12-BROWSER-AUTH-AND-MASKED-ACCESS-V1
- CAM-2026-03-12-METRICS-HOTPATH-AND-READ-PERF-V1
- CAM-2026-03-12-RUNTIME-DEPLANNERIZE-AND-BOOTSTRAP-HARDENING-V1
- CAM-2026-03-12-DOC-CODE-REALIGN-V1

## Parked
- CAM-2026-03-09-RUNTIME-DEPLANNERIZE-V1 (obsolete / already substantially delivered)

## Notes
- Current execution wave is imported from the owner-provided 2026-03-12 reference bundle and rebuilt in the main `work/` tree.
- `agent/intructions/DTM-test/**` is reference-only and not part of execution/archive lifecycle.
- Separate follow-ups remain outside this CAM:
  - `/info` build metadata 404 in `yc_function_info.py`
  - notify enqueue path inconsistency on test
