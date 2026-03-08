# Backlog

## In Progress
- none

## Planned
- CAM-FILE-ATTACHMENTS-V1

## Done
- CAM-TELEGRAM-INTAKE-V1
- CAM-GROUP-QUERY-UNIFY-WITH-REMINDER-V1
- CAM-ADMIN-ACTIONS-ASYNC-V1
- CAM-QUEUE-FOUNDATION-ON-CF-V1

## Parked
- none

## Notes
- Completed campaigns are stored in `work/archive/campaigns/`.
- `work/now/campaign.md` is the primary lifecycle registry; keep this file aligned with it.
- Queue foundation and async admin actions are live on test.
- Group query now reuses reminder milestone selection semantics and no longer owns a separate filtering path.
- Telegram webhook now validates secret token, enqueues commands, and uses worker-side `group_query_reply`.
