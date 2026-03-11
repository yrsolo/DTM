# Prometheus Integration

## Goal

Add a Prometheus-compatible second metrics sink so Grafana can become the primary human-facing dashboard while Yandex Monitoring remains the existing baseline sink.

## Selected backend policy

Current policy is dual write:

- keep `YandexMonitoringMetricsClient`
- add `YandexManagedPrometheusRemoteWriteClient`
- use `CompositeMetricsClient` when both are enabled

This preserves the current Monitoring-based observability and `/info` evidence while making Grafana possible without changing instrumentation points.

## Runtime topology

The runtime topology does not change:

- one deployed Cloud Function object per environment
- HTTP and MQ trigger handled by the same function object

Prometheus is only an additional metrics sink.

## Config

Typed config lives in:

- `config/runtime.yaml`
- `src/config/schema.py`
- `src/config/loader.py`

Prometheus section:

- `prometheus.enabled`
- `prometheus.backend`
- `prometheus.endpoint_write`
- `prometheus.folder_id`
- `prometheus.workspace_id_test`
- `prometheus.workspace_id_prod`
- `prometheus.service`
- `prometheus.namespace`
- `prometheus.timeout_seconds`

Current selected backend value:

- `yandex_managed_prometheus`

Current workspace policy:

- one shared Yandex Managed Prometheus workspace for both `test` and `prod`
- environment separation happens by metric label `env`

Grafana section:

- `grafana.enabled`
- `grafana.public_base_url`
- `grafana.dashboard_uid_test`
- `grafana.dashboard_uid_prod`
- `grafana.dashboard_url_test`
- `grafana.dashboard_url_prod`
- `grafana.embed_url_test`
- `grafana.embed_url_prod`
- `grafana.folder_name_test`
- `grafana.folder_name_prod`

## Backend behavior

`YandexManagedPrometheusRemoteWriteClient`:

- keeps the existing `MetricsClient` interface
- converts logical metric names to Prometheus-safe names by replacing dots with underscores
- writes samples through Prometheus Remote Write, not text exposition push
- keeps the same labels:
  - `env`
  - `module`
  - `operation`
  - `result`
- adds global labels:
  - `service="dtm"`
  - `namespace="dtm"`
- is nonfatal:
  - Prometheus write failures are logged
  - business operations must not fail because Prometheus is unavailable

Required secret:

- `YANDEX_PROMETHEUS_API_KEY`
- fallback legacy name: `YMP_API_KEY`

Secret resolution happens only in `src/app/bootstrap.py`.

## Metric name mapping

Examples:

- logical `dtm.snapshot.fetch_sheet_ms` -> Prometheus `dtm_snapshot_fetch_sheet_ms`
- logical `dtm.render.build_plan_ms` -> Prometheus `dtm_render_build_plan_ms`
- logical `dtm.api.requests_total` -> Prometheus `dtm_api_requests_total`

Monitoring names stay unchanged. Normalization happens only inside the Prometheus backend.

## Current rollout state

Repo-side remote-write foundation is implemented:

- typed config
- YMP Remote Write backend
- composite dual-write client
- additive `/info` metadata
- Grafana dashboard spec

Current live `test` facts:

- shared workspace id: `mon73oiiclfbmmqbjejn`
- write endpoint:
  - `https://monitoring.api.cloud.yandex.net/prometheus/workspaces/mon73oiiclfbmmqbjejn/api/v1/write`
- query endpoint:
  - `https://monitoring.api.cloud.yandex.net/prometheus/workspaces/mon73oiiclfbmmqbjejn/api/v1/query`
- Grafana datasource name:
  - `DTM YMP Test`

## Manual Yandex-side step

The remaining Yandex-side workspace creation is documented in:

- [yandex_prometheus_workspace_setup.md](n:\PROJECTS\python\SCRIPT\DTM\docs\system\yandex_prometheus_workspace_setup.md)

Datasource can be provisioned or updated from the repo with:

```powershell
python scripts/provision_grafana_datasource.py --env test --workspace-id mon73oiiclfbmmqbjejn
```

## Acceptance path

Remaining rollout path:

1. deploy `test` with `prometheus.enabled=true`
2. verify live sample ingestion into YMP
3. open Grafana dashboard and confirm non-empty panels

## Failure policy

Prometheus emission is best-effort only:

- failures log `prometheus_metric_flush_failed`
- Monitoring emission remains intact
- `/info` remains the operator control page regardless of Prometheus availability
