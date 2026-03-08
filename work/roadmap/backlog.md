# Backlog

## In Progress
- CAM-INFO-OPS-OBSERVABILITY-V1

## Planned
- none

## Done
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
- `/info` observability slice is live on `test`; render RCA shows queue+worker+apply path is healthy, and current remaining hotfix is the build-info adapter for function metadata.
- Queue foundation and async admin actions are live on test.
- Group query now reuses reminder milestone selection semantics and no longer owns a separate filtering path.
- Telegram webhook now validates secret token, enqueues commands, and uses worker-side `group_query_reply`.
- Attachment metadata now lives in snapshot extra-store, can be attached through queue command flow, and is exposed in API payloads without raw storage keys.
