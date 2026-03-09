# CAM-2026-03-09-OBSERVABILITY-FOUNDATION-V1

## Goal

Introduce a shared observability layer without rebuilding the existing `/info` dashboard.

## Scope

- `src/observability/metrics.py`
- `src/observability/timing.py`
- `src/observability/logging.py`
- additive instrumentation in active jobs and shells
- additive `/info` telemetry fields
- docs/tests

## Non-goals

- no second job-status subsystem
- no APM/tracing platform rollout
- no `/info` rewrite

## Implementation skeleton reference

- Primary source: current owner-approved plan in chat
- Trust level: high
- Existing baseline:
  - `/info` observability slice already exists
  - `src/worker/status_store.py` remains the source of truth for job status

## DoD

- `src/observability/*` exists and is used in active runtime
- snapshot/render/notify/api/telegram/worker boundaries have stable instrumentation points
- `/info` gains additive telemetry fields only
