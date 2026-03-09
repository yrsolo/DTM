# Campaign Priorities

## Priority 0
1. `CAM-2026-03-09-QUEUE-RETRY-SEMANTICS-V1`

## Priority 1
1. `CAM-2026-03-09-GREP-GATES-V1`
2. `CAM-2026-03-09-OBSERVABILITY-FOUNDATION-V1`

## Priority 2
1. `CAM-2026-03-09-TELEGRAM-COMMAND-ROUTER-V1`

## Priority 3
1. `CAM-2026-03-09-YC-MONITORING-INTEGRATION-V1`

## Obsolete / Already Delivered
- `CAM-2026-03-09-RUNTIME-DEPLANNERIZE-V1`
  - do not schedule as a new active campaign
  - standard runtime is already post-deplannerization

## Notes
- This is the only active priorities file.
- Queue retry semantics is the highest operational risk and goes first.
- Observability foundation extends current `/info`; it does not replace current job-status store.
- Telegram command router builds on the already thin enqueue-only webhook.
- YC Monitoring integration is a separate test-first rollout after observability foundation, not a replacement for `/info`.
