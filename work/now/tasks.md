# Active Tasks

- none

## Done

- CAM-GROUP-QUERY-UNIFY-WITH-REMINDER-V1 P01: replace `group_query_handler.py` filtering path with shared `ReminderUseCase.select()` flow
- CAM-GROUP-QUERY-UNIFY-WITH-REMINDER-V1 P02: add dedicated group-query formatter and remove payload-shaped task extraction assumptions
- CAM-GROUP-QUERY-UNIFY-WITH-REMINDER-V1 P03: update handler tests to build `PrepSnapshot` fixtures and prove today/next-workday parity
- CAM-ADMIN-ACTIONS-ASYNC-V1 P01: migrate `/info` admin buttons from sync runtime posts to enqueue endpoints
- CAM-ADMIN-ACTIONS-ASYNC-V1 P02: poll `/admin/jobs/{job_id}` and show real queued/running/succeeded/failed state in `/info`
- CAM-QUEUE-FOUNDATION-ON-CF-V1 P01: verified runtime touchpoints and marked campaign in progress
- CAM-QUEUE-FOUNDATION-ON-CF-V1 P02: implemented command DTO, serializer, queue config, and S3-backed job status store
- CAM-QUEUE-FOUNDATION-ON-CF-V1 P03: added queue event classifier, worker scaffolding, trigger enqueue fallback, and hidden admin enqueue/status endpoints
- CAM-QUEUE-FOUNDATION-ON-CF-V1 P04: created Yandex Message Queue test/prod queues and attached Cloud Function triggers
- CAM-QUEUE-FOUNDATION-ON-CF-V1 P05: deployed queue-enabled test contour and verified enqueue -> worker -> job status success path

## Notes

- Current `work/roadmap/campaigns/` contains only active or not-yet-archived campaign files.
- Historical completed task logs live in archived campaign evidence under `work/archive/campaigns/`.
- Keep only the current execution slice here; broader future CAM queue stays in `work/roadmap/campaigns/priorities.md`.
