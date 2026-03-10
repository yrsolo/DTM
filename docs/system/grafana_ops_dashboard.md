# Grafana Ops Dashboard

## Goal

Use Grafana as the primary human-facing operational dashboard over a Prometheus-compatible metrics source, while current Monitoring-based observability remains intact.

## Selected deployment model

- Grafana runs on the owner's VPS
- datasource is a Prometheus-compatible backend
- preferred target is Yandex Managed Service for Prometheus
- iframe embed is the selected presentation model for the owner's web page

## Repo role

The repo stores:

- Grafana metadata in typed config
- dashboard specification in `src/infra/grafana_specs.py`
- optional Grafana API helpers in `src/infra/grafana_api.py`
- dashboard JSON export script in `scripts/render_grafana_dashboard.py`

The repo is the source of truth for:

- panel names
- panel grouping
- query intent
- dashboard UID/URLs after provisioning

## Dashboard structure

The current dashboard spec contains 11 panels:

1. Snapshot Stage Timings
2. Snapshot Total Duration
3. Snapshot Outcomes
4. Render Stage Timings
5. Render Total Duration
6. Render Volume
7. API Latency
8. API Throughput
9. Worker Reliability
10. Notify Runtime
11. Telegram Intake

These panels are operator-oriented, not BI-oriented.

## Query conventions

Grafana panels query Prometheus-normalized metric names:

- `dtm_snapshot_fetch_sheet_ms`
- `dtm_snapshot_normalize_ms`
- `dtm_snapshot_build_prep_ms`
- `dtm_snapshot_write_raw_ms`
- `dtm_snapshot_write_prep_ms`
- `dtm_snapshot_update_duration_ms`
- `dtm_render_build_plan_ms`
- `dtm_render_write_sheet_ms`
- `dtm_render_duration_ms`
- `dtm_api_duration_ms`
- `dtm_api_requests_total`
- `dtm_worker_commands_total`
- etc.

Required label filters:

- `env="test"` for the test dashboard
- `namespace="dtm"`
- `service="dtm"`

Shared workspace note:

- `test` and `prod` use the same Yandex Managed Prometheus workspace
- dashboard separation is done by label filter `env`

## `/info` integration

`/info?format=json` exposes additive Grafana metadata:

- `grafanaEnabled`
- `grafanaBaseUrl`
- `grafanaDashboardUid`
- `grafanaDashboardUrl`
- `grafanaEmbedUrl`

This is for link-out and embed metadata only. `/info` is not being replaced by Grafana.

## Current rollout state

Repo-side Grafana foundation is implemented.

Current live test state:

- Grafana base URL: `http://style-app.solofarm.ru:3000`
- test folder: `DTM Test`
- imported dashboard UID: `dtm-test-ops`
- public dashboard URL: `http://style-app.solofarm.ru:3000/public-dashboards/af7606b66c8d4ca9b069ea1913577e45`
- embed URL: `http://style-app.solofarm.ru:3000/public-dashboards/af7606b66c8d4ca9b069ea1913577e45?kiosk&theme=light`

What is already done:

- API token auth works
- folder creation works
- dashboard import from repo spec works
- externally shared/public dashboard is created by API

What is still pending:

- datasource `DTM YMP Test` is created against workspace `mon73oiiclfbmmqbjejn`
- panel data will remain empty until the updated runtime emits samples into YMP
- Grafana server still returns `X-Frame-Options: deny`, so iframe embed remains blocked until `allow_embedding = true` is enabled on the VPS
- final workspace setup and datasource command are documented in:
  - [yandex_prometheus_workspace_setup.md](n:\PROJECTS\python\SCRIPT\DTM\docs\system\yandex_prometheus_workspace_setup.md)

## Export path

To render the current dashboard JSON from the repo spec:

```powershell
python scripts/render_grafana_dashboard.py --env test --output work/tmp/dtm_test_ops_dashboard.json
```

This file is intended for Grafana import or filesystem provisioning on the VPS once access is restored.

To create or update the live Prometheus datasource after the workspace exists:

```powershell
python scripts/provision_grafana_datasource.py --env test --workspace-id <workspace_id>
```

## Embed policy

Selected presentation:

- iframe embed

Recommended for `test`:

- externally shared/public dashboard URL
- no anonymous Grafana-wide access required
- no public admin surface
- `allow_embedding = true` still required on the Grafana server
- keep direct public dashboard URL as fallback until iframe headers are fixed
