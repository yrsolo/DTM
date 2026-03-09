# Yandex Monitoring Integration

## Topology

Current runtime topology stays unchanged:

- one deployed Cloud Function object per environment
- the same function handles:
  - HTTP gateway events
  - Message Queue trigger events

This integration does not introduce a separate worker function.

## Backend selection

Metrics emission goes through `MetricsClient`.

Bootstrap chooses the backend:

- `NoopMetricsClient` when monitoring is disabled
- `YandexMonitoringMetricsClient` when:
  - `runtime.monitoring.enabled=true`
  - `runtime.monitoring.backend=yandex_monitoring`

No service, job, or shell is allowed to branch on monitoring backend directly.

## Auth model

YC API auth is centralized in:

- `src/infra/yc_iam.py`

Current pattern:

- primary: bearer token from attached runtime service account via metadata endpoint
- fallback: service account JSON from runtime/deploy contour
- IAM token acquired via YC IAM API only when JSON key is used
- Monitoring writes authenticated with bearer IAM token

No interactive `yc` CLI auth is used inside runtime.

## Config

Typed config lives in:

- `config/runtime.yaml`
- `src/config/schema.py`
- `src/config/loader.py`

Key fields:

- `monitoring.enabled`
- `monitoring.backend`
- `monitoring.folder_id`
- `monitoring.endpoint_write`
- `monitoring.service`
- `monitoring.namespace`
- `monitoring.dashboard_name_test`
- `monitoring.dashboard_name_prod`
- `monitoring.dashboard_id_test`
- `monitoring.dashboard_id_prod`

Folder id resolution:

1. `runtime.monitoring.folder_id`
2. fallback `deploy.yandex_cloud.folder_id`

## Current backend behavior

`YandexMonitoringMetricsClient` sends custom metrics to:

- `https://monitoring.api.cloud.yandex.net/monitoring/v2/data/write`

Current service query for custom metrics:

- `service=custom`

Metrics failure policy:

- emission failures are nonfatal
- business path must not fail because Monitoring API is unavailable
- failures are logged as bounded structured warnings

## Test-first rollout policy

Current selected rollout:

1. enable real Monitoring backend on `test`
2. verify metric ingestion from live runtime
3. verify `/info` telemetry block
4. verify dashboard availability or explicitly record dashboard automation blocker
5. prepare prod separately after test evidence is clean

Current workflow defaults:

- test deploy enables monitoring
- prod release keeps monitoring disabled until explicit rollout

## Dashboard policy

Target dashboard names:

- `DTM Test Observability`
- `DTM Prod Observability`

Preferred widget groups:

- snapshot
- api
- render
- notify
- telegram
- worker / queue

Current status:

- custom metrics write path is verified
- dashboard automation may remain unsupported in v1 if YC API access is insufficient or endpoint contract is unavailable

That is not allowed to block metric ingestion itself.

## Smoke checklist

For test contour:

1. deploy function with monitoring enabled
2. open `/info?format=json`
3. verify:
   - `telemetry.metricsEnabled=true`
   - `telemetry.monitoringBackend=yandex_monitoring`
4. hit `/api/v2/frontend`
5. enqueue:
   - timeline render
   - reminders
6. hit Telegram webhook accepted path
7. verify custom metrics appear in Yandex Monitoring with `env=test`
8. record evidence:
   - metric names
   - dashboard id/name if available
   - function version/time window

## Failure triage

If metrics do not appear:

1. verify monitoring is enabled in runtime env
2. verify folder id is resolved correctly
3. verify attached runtime service account has Monitoring write permission
4. inspect structured warning logs for:
   - `monitoring_metric_emit_failed`
5. verify endpoint and network access

If dashboard is missing:

1. verify dashboard id config
2. verify dashboard automation permissions
3. if automation is unsupported, create dashboard manually and record id in evidence/config
