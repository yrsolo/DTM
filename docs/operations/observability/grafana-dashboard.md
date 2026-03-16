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

The current dashboard spec contains:

- a dense top stat section for snapshot, render, info, and wall-clock/flush diagnostics
- compact timeseries panels for snapshot/render/API/info/worker/notify/telegram/flush activity
- dedicated frontend bottleneck panels for stage breakdown, route comparison, and cache hit/miss/bypass comparison
- dedicated direct `/api` outer-latency panels for function/shell/dispatch timing versus inner frontend stages

These panels are operator-oriented, not BI-oriented.

Current layout policy:

- single-value stat panels use compact `2x2` cards so more current-state diagnostics fit on screen
- timeseries panels use `6` grid columns instead of full-width `12` where possible
- the repo dashboard spec is expected to stay denser than the default Grafana layout

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

## Stat panel aggregation policy

The dashboard uses raw metrics only.

### `last`
- derived by query using `last_over_time(...[7d])`

### `avg5`
- derived in Grafana panel transformations from raw time series
- panel flow:
  1. query raw metric series
  2. convert series to rows
  3. sort by timestamp descending
  4. limit to 5 rows
  5. reduce with mean

This keeps raw stage timings as the only canonical runtime metrics.

### Wall-clock and flush stats

The dashboard also shows raw-metric stat panels for:

- `Snapshot Business Duration`
- `Snapshot Job Wall Clock`
- `Worker Wall Clock`
- `Metrics Flush Total`
- `Info Summary Last`
- `Info Detail Last`
- `Orphan Reconcile Last`

This is intentional: operator questions about "why button wall-clock is larger than business stage timings" should be answered on the dashboard, not inferred manually from logs.

### Render stat panels

Render stat panels are explicit by operation:
- `timeline`
- `designers`

They are not merged with `max(...)`, because that would hide which render path is slow.

## `/info` integration

`/info` remains the operator control surface and summary view.

`/info?format=json` exposes additive Grafana metadata:

- `grafanaEnabled`
- `grafanaBaseUrl`
- `grafanaDashboardUid`
- `grafanaDashboardUrl`
- `grafanaEmbedUrl`

This is for link-out and embed metadata only. `/info` is not being replaced by Grafana.

Current `/info` UI policy:

- default operator view is summary-first
- heavy JSON/detail inspection is explicit
- `Recent Jobs`, `Admin Actions`, `API Request Builder`, and `Info JSON` stay collapsible and default-closed so dashboard-level information fits on one screen more easily
- `/info` detail also exposes recent in-process frontend stage traces and current profiling level as a secondary diagnostics surface
- `/info` detail also exposes recent direct `/api` outer traces so operator checks can compare `function total`, `router precheck`, `router handler`, `frontend handler total`, `frontend inner core`, and the unexplained gaps inside/after the handler without changing payload contracts

## Current rollout state

Repo-side Grafana foundation is implemented.

Current verified test state:

- Grafana base URL: `https://dtm.solofarm.ru/grafana`
- test folder: `DTM Test`
- imported dashboard UID: `dtm-test-ops`
- public dashboard URL: `https://dtm.solofarm.ru/grafana/public-dashboards/af7606b66c8d4ca9b069ea1913577e45`
- embed URL: `https://dtm.solofarm.ru/grafana/public-dashboards/af7606b66c8d4ca9b069ea1913577e45?kiosk&theme=light`
- datasource: `DTM YMP Test`
- shared YMP workspace: `mon73oiiclfbmmqbjejn`

What is already done:

- API token auth works
- folder creation works
- dashboard import from repo spec works
- externally shared/public dashboard is created by API
- dashboard layout is republished from `src/infra/grafana_specs.py`, not hand-edited in Grafana
- current public dashboard includes compact stat cards and separate info/flush panels
- current repo dashboard spec also includes direct `/api` outer breakdown and outer-vs-inner comparison panels for latency decomposition work

Current operational caveats:

- iframe embed still depends on Grafana server-side `allow_embedding = true`
- raw metric samples still require datasource/query access; the public dashboard is not a substitute for direct Monitoring queries
- final workspace setup and datasource command are documented in:
  - [yandex-prometheus-workspace-setup.md](yandex-prometheus-workspace-setup.md)

Sparse metric visualization policy:

- timeseries panels use lines only (`showPoints = never`)
- stat panels are preferred for "current" and "avg5" operator reading
- render stat panels are separated by `timeline` and `designers`; they are not merged

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
