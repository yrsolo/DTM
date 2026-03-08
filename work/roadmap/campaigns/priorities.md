# Campaign Priorities

## Priority 0
1. `CAM-INFO-OPS-OBSERVABILITY-V1`

## Priority 1
1. `CAM-QUEUE-FOUNDATION-ON-CF-V1`
2. `CAM-ADMIN-ACTIONS-ASYNC-V1`
3. `CAM-GROUP-QUERY-UNIFY-WITH-REMINDER-V1`

## Priority 2
1. `CAM-TELEGRAM-INTAKE-V1`

## Priority 3
1. `CAM-FILE-ATTACHMENTS-V1`

## Notes
- This is the only active priorities file.
- `/info` observability comes first because render debugging is blocked without it.
- Queue foundation is already delivered and is the dependency base for current ops work.
- Telegram runtime rollout is deferred until queue foundation is stable.
- File attachments stay after queue and job-status contours are proven.
