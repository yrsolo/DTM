# CAM-2026-03-09-YC-MONITORING-INTEGRATION-V1

## Goal

Turn the existing observability foundation into a real external metrics backend using Yandex Monitoring custom metrics, starting with the test contour.

## Scope

- typed monitoring config
- shared YC IAM helper for Monitoring and other YC API adapters
- real `YandexMonitoringMetricsClient`
- bootstrap backend selection
- additive `/info` telemetry fields
- test deploy enablement and test smoke evidence

## Non-goals

- no tracing/APM rollout
- no `/info` rewrite
- no replacement of job status store
- no prod rollout in the same change set

## Implementation skeleton reference

- Primary source: owner-approved execution plan in chat
- Trust level: high for code baseline, medium for live YC-side permissions until smoke is captured
- Existing baseline:
  - `src/observability/*`
  - `src/app/bootstrap.py`
  - `src/infra/yc_function_info.py`
  - `/info` telemetry block already exists

## DoD

- active runtime in test contour uses `YandexMonitoringMetricsClient`
- already instrumented paths emit custom metrics to Yandex Monitoring
- `/info` exposes additive monitoring metadata
- docs/runbook/evidence reflect the real test-first contour
