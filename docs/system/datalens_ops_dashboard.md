# DataLens Ops Dashboard

## Purpose
Provide a test-first operator dashboard in Yandex DataLens over existing Yandex Monitoring custom metrics.

## Provisioning mode
- API-first via DataLens Public API
- Monitoring connection + workbook + charts + dashboard
- UI fallback only if API permissions or object semantics block automation

## Current naming
- Workbook: `DTM Observability`
- Test connection: `DTM Monitoring Test`
- Prod connection: `DTM Monitoring Prod`
- Test dashboard: `DTM Test Ops`
- Prod dashboard: `DTM Prod Ops`

## Chart groups
- snapshot stage timings and total duration
- snapshot outcome counters
- render stage timings, total duration, volume
- API latency and throughput
- worker reliability
- notify runtime
- telegram intake

## Notes
- DataLens is a visualization layer over Monitoring metrics, not a second metrics source.
- Use `env=test` filters in the test dashboard.
- Avoid workbook JSON import/export as the primary path for Monitoring-backed dashboards.
- Current live status:
  - workbook creation: proven
  - Monitoring connection creation: proven
  - QL chart creation through Public API: currently blocked by `500 Access service error` on the Monitoring connection
  - caller-side folder permissions were explicitly tested (`viewer` + `monitoring.viewer`) and did not change the failure mode
