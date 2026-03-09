# Backlog

## In Progress
- none

## Planned
- none

## Done
- CAM-LEGACY-ARCHIVE-CLEANUP-V1
- CAM-ENTRYPOINT-LEGACY-CUT-FINAL-V1
- CAM-INFO-OPS-OBSERVABILITY-V1
- CAM-FILE-ATTACHMENTS-V1
- CAM-TELEGRAM-INTAKE-V1
- CAM-GROUP-QUERY-UNIFY-WITH-REMINDER-V1
- CAM-ADMIN-ACTIONS-ASYNC-V1
- CAM-QUEUE-FOUNDATION-ON-CF-V1

## Parked
- none

## Notes
- Completed campaigns are stored in `work/archive/campaigns/`.
- `work/now/campaign.md` is the primary lifecycle registry; keep this file aligned with it.
- `/info` observability slice is live on `test`; render RCA showed queue+worker+apply path is healthy.
- Queue foundation and async admin actions are live on test.
- Group query now reuses reminder milestone selection semantics and no longer owns a separate filtering path.
- Telegram webhook now validates secret token, enqueues commands, and uses worker-side `group_query_reply`.
- Attachment metadata now lives in snapshot extra-store, can be attached through queue command flow, and is exposed in API payloads without raw storage keys.
- Standard runtime entrypoints now run through `IndexDispatcher` + transport shells; legacy planner/store/readmodel-probe branches are no longer part of standard runtime.
