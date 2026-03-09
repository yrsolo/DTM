# Active Tasks

- CAM-SNAPSHOT-RENDER-TIMINGS-V1 P01: add detailed snapshot timings for fetch/normalize/build_prep/write_raw/write_prep and surface them through metrics and job result
- CAM-SNAPSHOT-RENDER-TIMINGS-V1 P02: add detailed render timings for build_plan/write_sheet/total and surface them through metrics and job result

## Done

- CAM-2026-03-09-QUEUE-RETRY-SEMANTICS-V1 P01: extend worker result/status vocabulary to retryable vs terminal failures
- CAM-2026-03-09-QUEUE-RETRY-SEMANTICS-V1 P02: update dispatcher/worker/worker-shell semantics and add retry-focused tests
- CAM-2026-03-09-GREP-GATES-V1 P01: extend forbidden-import guard to telegram/commands/worker/observability scopes
- CAM-2026-03-09-GREP-GATES-V1 P02: wire legacy guard scripts into test/prod deploy workflows
- CAM-2026-03-09-OBSERVABILITY-FOUNDATION-V1 P01: add shared observability modules for metrics, timing, and structured logging
- CAM-2026-03-09-OBSERVABILITY-FOUNDATION-V1 P02: instrument snapshot/render/notify/http boundaries and expose additive telemetry info in `/info`
- CAM-2026-03-09-TELEGRAM-COMMAND-ROUTER-V1 P01: add typed Telegram DTOs and dedicated command router
- CAM-2026-03-09-TELEGRAM-COMMAND-ROUTER-V1 P02: keep webhook enqueue-only while splitting parser and router responsibilities
- CAM-2026-03-09-TELEGRAM-COMMAND-ROUTER-V1 P03: add parser/router tests and align docs/tracking with current post-legacy baseline
- CAM-2026-03-09-YC-MONITORING-INTEGRATION-V1 P01: add typed monitoring config, YC IAM helper, and real Yandex Monitoring metrics client
- CAM-2026-03-09-YC-MONITORING-INTEGRATION-V1 P02: wire monitoring backend in bootstrap, add docs, and create/update test Yandex Monitoring dashboard
- CAM-2026-03-09-YC-MONITORING-INTEGRATION-V1 P03: deploy monitoring-enabled test contour and capture live metric emission evidence from `/info`, API, and render on the real test function

## Notes

- `CAM-2026-03-09-RUNTIME-DEPLANNERIZE-V1` is not opened as active work because the runtime is already post-deplannerization after the legacy-cut sequence.
- Monitoring integration is considered complete for test-first scope; notify enqueue inconsistency and `/info` build 404 remain separate follow-up issues.
