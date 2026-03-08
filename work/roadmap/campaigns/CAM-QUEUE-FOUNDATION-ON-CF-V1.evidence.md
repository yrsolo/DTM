# Evidence - CAM-QUEUE-FOUNDATION-ON-CF-V1

## Trust Gate

- source:
  - `index.py`
  - `src/entrypoints/runtime/planner_runtime_entry.py`
  - `src/entrypoints/http/info_handler.py`
  - `src/services/timer_pipeline.py`
  - `src/snapshot_engine/engine.py`
- last_verified_at: 2026-03-08
- verified_by: codex
- trust_level: medium-high
- evidence:
  - HTTP path is already thin in `index.py`, but heavy execution still routes through runtime request handling.
  - admin `/info` currently triggers sync execution of `sync-only`, `render_v2`, and reminder modes.
  - snapshot engine is already canonical for read path and update path orchestration.
  - runtime still centralizes heavy mode switching in `planner_runtime_entry.py`.

## Notes

- Primary implementation source doc: `docs/system/command_queue_skeleton.md`
- Current state: partially implemented foundation, not yet activated in cloud.

## Execution Update - 2026-03-08

- implemented:
  - `src/commands/*` command DTO, serializer, type registry, and Yandex MQ producer/event parser
  - `src/worker/*` job status store, dispatcher, and queue-trigger worker
  - `src/jobs/update_snapshot_job.py`
  - `src/jobs/send_reminders_job.py`
  - `src/jobs/render_timeline_job.py`
  - `src/jobs/render_designers_job.py`
  - `src/entrypoints/http/admin_queue_handler.py`
  - `src/entrypoints/http/job_status_handler.py`
  - bootstrap wiring under `queue.enabled=true`
  - queue-trigger event handling in `index.py`
  - trigger enqueue fallback for `timer -> update_snapshot` and `morning -> send_reminders`
- preserved:
  - `/info` buttons still use sync execution and are not yet migrated
  - direct sync HTTP/runtime paths still remain available as compatibility path
- infra configured:
  - test queue: `dtm-test-commands`
  - prod queue: `dtm-prod-commands`
  - test trigger: `dtm-test-commands-trigger` -> function `dtm`
  - prod trigger: `dtm-prod-commands-trigger` -> function `dtm-prod`
  - trigger ids:
    - `a1smv307dc6tmas6ni0r`
    - `a1scnkiiivkcpj4fv077`
  - queue URLs persisted in `config/runtime.yaml`
- trigger API note:
  - Yandex Cloud trigger creation expects queue identifier in form `yrn:yc:ymq:ru-central1:<folder-id>:<queue-name>`
- permission note:
  - current key allows queue creation/listing, but not queue attribute introspection/update
  - DLQ linkage should be treated as follow-up hardening, not current foundation blocker
- tests:
  - `python -m unittest tests.api.test_command_queue_foundation -v`
  - `python -m unittest tests.api.test_frontend_api_routing -v`
  - `python -m unittest tests.api.test_runtime_execution -v`
  - all passed

## Current Status

- Queue infra is configured.
- Next execution step is queue-enabled deploy to `test` and cloud smoke of:
  - admin enqueue endpoint
  - MQ-triggered worker path
  - S3 job status updates
