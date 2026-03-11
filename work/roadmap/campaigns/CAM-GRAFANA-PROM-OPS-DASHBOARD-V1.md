# CAM-GRAFANA-PROM-OPS-DASHBOARD-V1

## Goal

Create a Grafana-based operator dashboard for the current metrics stack by adding a real Yandex Managed Prometheus remote-write second sink and exposing Grafana metadata for iframe embed.

## Scope

- typed `prometheus` and `grafana` config
- Yandex Managed Prometheus remote-write backend
- dual-write `CompositeMetricsClient`
- Grafana dashboard spec and API helpers
- one-command Grafana datasource provisioning from repo once workspace metadata exists
- additive `/info` telemetry fields for Prometheus/Grafana
- docs, runbook, and evidence

## Non-goals

- no replacement of Yandex Monitoring
- no alerting rollout
- no prod rollout in the same change set
- no custom frontend chart rendering

## Implementation skeleton reference

- Primary source: owner-approved execution plan in chat
- Trust level: high for repo-side metrics/observability baseline, medium for live Yandex Prometheus and VPS Grafana infra until live smoke succeeds
- Existing baseline:
  - `src/observability/metrics.py`
  - `src/infra/yc_monitoring.py`
  - `/info` telemetry block
  - live Monitoring metrics and dashboard already proven on `test`

## DoD

- active runtime can dual-write metrics to Monitoring and Yandex Managed Prometheus through Remote Write
- `/info` exposes additive Prometheus/Grafana metadata
- Grafana dashboard spec exists in repo for snapshot/render/API/worker/notify/telegram panels
- repo provides a self-service datasource provisioning command once `workspace_id` is known
- docs/evidence capture the current infra blockers and the accepted rollout path
