# Active Tasks

- none

## Done

- CAM-LEGACY-ARCHIVE-CLEANUP-V1 P01: verified `main.py` is only used by `local_run.py` and old planner/readmodel-probe stack is not needed by live features
- CAM-LEGACY-ARCHIVE-CLEANUP-V1 P02: added `local_runtime.py`, switched `local_run.py`, and archived `main.py`
- CAM-LEGACY-ARCHIVE-CLEANUP-V1 P03: moved planner/bootstrap/render/readmodel-probe modules under `src/legacy/`
- CAM-LEGACY-ARCHIVE-CLEANUP-V1 P04: rewired compatibility/tooling imports and tightened legacy import guard
- CAM-LEGACY-ARCHIVE-CLEANUP-V1 P05: archived compat `core/bootstrap.py`, `core/manager.py`, planner use-case shim, and moved legacy tests under `tests/legacy/`
- CAM-LEGACY-ARCHIVE-CLEANUP-V1 P06: updated docs/tracking and re-ran smoke/regression checks
- CAM-LEGACY-ARCHIVE-CLEANUP-V1 P07: archived stale active system docs to `docs/archive/system_legacy/` and rewrote active `docs/system/*` to current runtime state

- CAM-ENTRYPOINT-LEGACY-CUT-FINAL-V1 P01: register campaign, trust gate, and verified runtime/entrypoint cut line
- CAM-ENTRYPOINT-LEGACY-CUT-FINAL-V1 P02: thin `index.py` into dispatcher + transport shells and remove `FrontendReadmodelRepo` leak
- CAM-ENTRYPOINT-LEGACY-CUT-FINAL-V1 P03: cut legacy planner/store/readmodel probe branch from standard runtime
- CAM-ENTRYPOINT-LEGACY-CUT-FINAL-V1 P04: archive dead-end legacy entrypoint jobs and add grep gate
- CAM-ENTRYPOINT-LEGACY-CUT-FINAL-V1 P05: run routing/runtime regression tests, update docs, and close campaign

- CAM-INFO-OPS-OBSERVABILITY-V1 P08: deploy build-info hotfix to `test`, verify `/info.build` is populated, then close campaign

- CAM-INFO-OPS-OBSERVABILITY-V1 P01: register campaign, trust gate, and verified touchpoints for `/info`, queue status, and render diagnostics
- CAM-INFO-OPS-OBSERVABILITY-V1 P02: extend `S3JobStatusStore` with recent terminal history and accessors
- CAM-INFO-OPS-OBSERVABILITY-V1 P03: add live Yandex queue/function info adapters and surface them in `/info?format=json`
- CAM-INFO-OPS-OBSERVABILITY-V1 P04: expand `/info` HTML with build, queue state, recent jobs, and last render job panels
- CAM-INFO-OPS-OBSERVABILITY-V1 P05: enrich `render_timeline_sheet` result with counters/no-op reasons and derive `renderDebug`
- CAM-INFO-OPS-OBSERVABILITY-V1 P06: run focused tests and capture evidence for render failure triage
- CAM-INFO-OPS-OBSERVABILITY-V1 P07: deploy observability slice to `test`, inspect `/info`, trigger live `render_timeline_sheet`, and determine the actual RCA branch

- CAM-FILE-ATTACHMENTS-V1 P01: add attachment metadata model and S3 serialization/store support in snapshot extra-store
- CAM-FILE-ATTACHMENTS-V1 P02: add `attach_task_file` command type, worker job, and snapshot-engine prep refresh flow
- CAM-FILE-ATTACHMENTS-V1 P03: add hidden upload-contract/enqueue endpoint and expose attachment metadata in snapshot-backed API payload/docs
- CAM-FILE-ATTACHMENTS-V1 P04: cover attach flow with store/job/API tests and record evidence
- CAM-TELEGRAM-INTAKE-V1 P01: add telegram config and trust-gated webhook parser/handler modules
- CAM-TELEGRAM-INTAKE-V1 P02: switch `/telegram` HTTP path to secret-validated enqueue-only webhook flow
- CAM-TELEGRAM-INTAKE-V1 P03: add `group_query_reply` worker job so webhook no longer executes business logic inline
- CAM-TELEGRAM-INTAKE-V1 P04: expose webhook config block in `/info` and cover intake/job behavior with tests
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
