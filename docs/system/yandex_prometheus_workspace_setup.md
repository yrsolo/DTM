# Yandex Managed Prometheus Workspace Setup

## Purpose

This runbook records the Yandex-side setup for the Grafana dashboard rollout:

1. use the single Managed Service for Prometheus workspace used by both `test` and `prod`
2. create a service account API key for read/write
3. persist the workspace metadata into DTM config
4. create the Grafana datasource with one repo script

This document assumes the repo already contains:

- real YMP Remote Write support
- Grafana dashboard `dtm-test-ops`
- Grafana API token in `.env`

## Current target values

Use these exact names to avoid drift:

- service account: `dtm-prometheus-test`
- Grafana datasource: `DTM YMP Test`
- Grafana dashboard UID: `dtm-test-ops`

Workspace fact confirmed by owner:

- workspace is global/singleton for this setup
- current workspace id: `mon73oiiclfbmmqbjejn`

Folder already used by DTM:

- `b1g42qj26s1u7gv7bufm`

## Step 1 - Use the shared workspace in Yandex Cloud UI

At the time of writing, this step is treated as a UI step rather than a stable `yc` CLI flow.

Open Yandex Cloud console:

- Monitoring
- Prometheus
- Shared workspace id:
  - `mon73oiiclfbmmqbjejn`

## Step 2 - Create or confirm service account and API key

Recommended service account:

- `dtm-prometheus-test`

Required roles on the folder:

- `monitoring.editor`
- `monitoring.viewer`

Store the API key only in `.env`:

```env
YANDEX_PROMETHEUS_API_KEY=...
```

Legacy fallback name still supported by bootstrap:

```env
YMP_API_KEY=...
```

Recommended canonical name remains:

- `YANDEX_PROMETHEUS_API_KEY`

## Step 3 - Persist workspace metadata in config

Update [runtime.yaml](n:\PROJECTS\python\SCRIPT\DTM\config\runtime.yaml):

```yaml
prometheus:
  enabled: true
  backend: yandex_managed_prometheus
  endpoint_write: https://monitoring.api.cloud.yandex.net/prometheus/workspaces/mon73oiiclfbmmqbjejn/api/v1/write
  folder_id: b1g42qj26s1u7gv7bufm
  workspace_id_test: mon73oiiclfbmmqbjejn
  workspace_id_prod: mon73oiiclfbmmqbjejn
  service: dtm
  namespace: dtm
  timeout_seconds: 2.0
```

Notes:

- write endpoint is `.../api/v1/write`
- Grafana datasource will use query endpoint `.../api/v1/query`

## Step 4 - Create Grafana datasource from the repo

Once `.env` contains:

- `GRAFANA_TOKEN`
- `YANDEX_PROMETHEUS_API_KEY`

run:

```powershell
python scripts/provision_grafana_datasource.py --env test --workspace-id mon73oiiclfbmmqbjejn
```

This will:

- compute the YMP query endpoint
- create or update Grafana datasource `DTM YMP Test`

Expected query endpoint:

```text
https://monitoring.api.cloud.yandex.net/prometheus/workspaces/mon73oiiclfbmmqbjejn/api/v1/query
```

## Step 5 - Verify Grafana

Open Grafana:

- dashboard: `http://style-app.solofarm.ru:3000/d/dtm-test-ops/dtm-test-ops`
- embed: `http://style-app.solofarm.ru:3000/d/dtm-test-ops/dtm-test-ops?kiosk&theme=light`

Check that these panels are non-empty after live actions:

1. `Snapshot Stage Timings`
2. `Snapshot Total Duration`
3. `Render Stage Timings`
4. `Render Total Duration`
5. `API Latency`
6. `Worker Reliability`

If panels stay empty:

1. confirm datasource `DTM YMP Test` exists and `Save & Test` passes
2. confirm `prometheus.enabled=true` on `test`
3. confirm `YANDEX_PROMETHEUS_API_KEY` is available to runtime
4. trigger:
   - one `/api/v2/frontend`
   - one snapshot update
   - one timeline render

## Step 6 - Verify `/info`

Open:

- `/info?format=json`

Expected telemetry fields:

- `prometheusEnabled=true`
- `prometheusBackend=yandex_managed_prometheus`
- `prometheusWorkspaceId=mon73oiiclfbmmqbjejn`
- `grafanaEnabled=true`
- `grafanaDashboardUid=dtm-test-ops`
- `grafanaDashboardUrl=http://style-app.solofarm.ru:3000/d/dtm-test-ops/dtm-test-ops`
- `grafanaEmbedUrl=http://style-app.solofarm.ru:3000/d/dtm-test-ops/dtm-test-ops?kiosk&theme=light`

## Notes

- Yandex Monitoring remains the baseline sink; Prometheus is the second sink.
- Workspace is shared; separation between `test` and `prod` is done by metric label `env`.
- Do not place Prometheus API keys into YAML.
