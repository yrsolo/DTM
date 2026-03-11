# CAM-INFO-OPS-OBSERVABILITY-V1

## Goal

Turn `/info` into a real operational dashboard for async execution and render debugging.

## Scope

- extend S3 job status store from latest-only to latest + recent history
- add live queue state block from Yandex Message Queue
- add live function build/version block from Yandex Cloud Functions metadata
- extend render timeline job result with debugging-grade counters and no-op reasons
- surface queue/build/jobs/renderDebug blocks in `/info?format=json`
- surface queue/build/recent jobs/last render status in HTML `/info`

## Non-goals

- no UI framework migration
- no render logic rewrite in this CAM
- no queue/admin behavior change beyond observability
- no unrelated telemetry stack

## Implementation Skeleton Reference

- Primary implementation skeleton: owner-approved plan in current chat
- Current trust level: high after verification against live runtime files
- Current runtime touchpoints:
  - `src/entrypoints/http/info_handler.py`
  - `src/worker/status_store.py`
  - `src/jobs/render_timeline_job.py`
  - `src/render/usecase.py`
  - `src/render/job.py`
  - `src/render/sheets_adapter.py`
  - `src/commands/yandex_mq.py`
  - `src/app/bootstrap.py`
- Forbidden shortcuts:
  - blind render bug fixing before observability exists
  - replacing `/info` with a new UI stack
  - introducing YDB for job history

## Phases

1. Trust gate and campaign registration
2. Status store history support
3. Live queue/function info adapters
4. `/info` JSON + HTML observability expansion
5. Render result diagnostics expansion
6. Evidence-driven render investigation

## DoD

- `/info?format=json` includes `build`, `queue.live`, `jobs.recent`, and `renderDebug`
- `/info` HTML shows function build, queue state, recent jobs, and last render job
- terminal jobs are persisted in short recent history
- last render job result is sufficient to distinguish `blocked|failed|noop|applied`
- render failure investigation can proceed from evidence instead of guesswork
