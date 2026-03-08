# Evidence - CAM-INFO-OPS-OBSERVABILITY-V1

## Trust Gate

- source:
  - `src/entrypoints/http/info_handler.py`
  - `src/worker/status_store.py`
  - `src/jobs/render_timeline_job.py`
  - `src/render/usecase.py`
  - `src/render/job.py`
  - `src/render/sheets_adapter.py`
  - `src/commands/yandex_mq.py`
  - `src/app/bootstrap.py`
  - `tests/api/test_frontend_api_routing.py`
  - `tests/api/test_command_queue_foundation.py`
- last_verified_at: 2026-03-09
- verified_by: codex
- trust_level: high
- evidence:
  - `/info` currently shows snapshot/storage/latest job summaries only; no live queue depth, no build metadata, no recent job history.
  - `S3JobStatusStore` currently persists `status/{job_id}.json` and `latest/{command_type}.json` only.
  - `render_timeline_sheet` result currently exposes only applied/rows/cells/target/warnings and cannot explain no-op vs blocked vs failed in enough detail.
  - queue producer already uses SQS-compatible Yandex MQ access, so the same auth path can read queue attributes live.
  - build metadata path is not yet present; this CAM must add a fail-soft adapter.

## Notes

- This CAM intentionally improves observability before attempting any render bug fix.
- Build metadata adapter may degrade gracefully if runtime credentials are insufficient for Yandex Cloud Functions API calls.

## Implementation Evidence

- implemented:
  - `src/worker/status_store.py`
    - added recent terminal history:
      - `jobs/{env}/history/index.json`
      - `jobs/{env}/history/by-command/{command_type}.json`
    - `put_finished(...)` now appends terminal records into history
  - `src/infra/yc_queue_info.py`
    - live queue attribute adapter over Yandex MQ SQS-compatible API
  - `src/infra/yc_function_info.py`
    - live Cloud Function build metadata adapter over Yandex IAM + Functions API
  - `src/entrypoints/http/info_handler.py`
    - `build`
    - `queue.live`
    - `jobs.recent`
    - `jobs.failedRecent`
    - `jobs.latestByCommand`
    - `renderDebug`
    - HTML sections:
      - `Function Build`
      - `Queue State`
      - `Recent Jobs`
      - `Last Errors`
      - `Last Render Job`
      - `Render Debug`
  - `src/jobs/render_timeline_job.py`
    - richer counters and explicit blocked/no-op semantics for render diagnostics

## Local Verification

- last_verified_at: 2026-03-09
- verified_by: codex
- trust_level: high
- evidence:
  - `python -m unittest tests.worker.test_status_store_history -v`
  - `python -m unittest tests.api.test_info_observability -v`
  - `python -m unittest tests.api.test_frontend_api_routing -v`
  - `python -m unittest tests.render.test_render_v2 -v`
- result:
  - all targeted tests passed
  - `/info` JSON/HTML contract is now covered for build/queue/jobs/renderDebug blocks
  - render result contract is locally rich enough for RCA

## Remaining Work

- deploy this slice to `test`
- inspect `/info` on live runtime
- capture last `render_timeline_sheet` job record and derive root cause branch:
  - queue backlog
  - worker failure
  - target guard block
  - no-op
  - applied-to-wrong-target
