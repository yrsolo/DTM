# CAM-GRAFANA-PROM-OPS-DASHBOARD-V1 Evidence

## Trust gate

- source: active runtime code, current observability modules, local YC CLI probes, current `test` Monitoring evidence, VPS access attempts
- last_verified_at: 2026-03-10
- verified_by: Codex
- evidence:
  - `src/observability/metrics.py`
  - `src/app/bootstrap.py`
  - `src/entrypoints/http/info_handler.py`
  - `docs/system/metrics_schema.md`
  - local `yc` CLI probes for DataLens and Compute
  - current Monitoring test dashboard evidence
- trust_level: medium
- notes:
  - repo-side observability baseline is stable and verified
- current Yandex Managed Prometheus workspace id and final write/query endpoints are still external infra facts, not repo facts
- Grafana dashboard provisioning by API is already proven; the remaining live dependencies are YMP workspace/API key and datasource wiring
- workspace policy is now verified:
  - one shared workspace is used for both `test` and `prod`
  - environment split is by metric label `env`

## Verified baseline facts

- runtime already emits metrics through `MetricsClient`
- Monitoring custom metrics are live on `test`
- snapshot and render stage timings are already instrumented
- `/info` already exposes additive telemetry metadata
- DataLens chart provisioning over Monitoring connection is externally blocked and should not be the primary dashboard path

## Repo-side implementation state

- typed config added for:
  - `runtime.prometheus`
  - `runtime.grafana`
- dual-write abstractions added:
  - `src/observability/prometheus_metrics.py`
  - `src/observability/composite_metrics.py`
- bootstrap now supports:
  - Monitoring only
  - Prometheus only
  - Monitoring + Prometheus dual write
- additive `/info` telemetry fields added for:
  - Prometheus backend/workspace metadata
  - Grafana base URL/dashboard/embed metadata
- Grafana dashboard spec added for:
  - snapshot stage timings
  - render stage timings
  - API
  - worker
  - notify
  - telegram
- repo-assisted datasource rollout added:
  - `scripts/provision_grafana_datasource.py`
  - `docs/system/yandex_prometheus_workspace_setup.md`
- trust status for current Prometheus code path: low
  - evidence:
    - `src/observability/prometheus_metrics.py`
    - `src/infra/yc_prometheus.py`
  - notes:
    - current implementation uses generic text exposition push
    - this is insufficient for Yandex Managed Prometheus, which requires real Prometheus Remote Write protocol
    - current execution slice is therefore a verification-and-replacement task, not infra rollout yet
- remote-write replacement status: done
  - evidence:
    - `src/infra/yc_prometheus.py`
    - `src/observability/prometheus_metrics.py`
    - `tests/observability/test_prometheus_metrics.py`
    - `tests/app/test_bootstrap_monitoring.py`
  - notes:
    - active bootstrap path no longer uses text exposition push for `yandex_managed_prometheus`
    - runtime now resolves `YANDEX_PROMETHEUS_API_KEY` with `YMP_API_KEY` fallback
    - remaining live rollout blocker is workspace/API key/datasource setup, not protocol support inside repo

## Live infra blockers

### 1) Shared Yandex Managed Prometheus workspace is finalized

- repo now expects a real workspace-specific remote-write endpoint:
  - `https://monitoring.api.cloud.yandex.net/prometheus/workspaces/<workspace_id>/api/v1/write`
- verified shared workspace id:
  - `mon73oiiclfbmmqbjejn`
- verified direct query endpoint response:
  - `https://monitoring.api.cloud.yandex.net/prometheus/workspaces/mon73oiiclfbmmqbjejn/api/v1/query?query=1`
  - HTTP `200`
  - Prometheus API payload returned successfully

### 2) Grafana datasource is configured

- Grafana itself is already live at:
  - `http://style-app.solofarm.ru:3000`
- folder `DTM Test` and dashboard `dtm-test-ops` already exist
- datasource `DTM YMP Test` created from repo script
- datasource id: `3`
- datasource uid: `effm65zf51xc0b`

## Current conclusion

- repo-side Grafana/YMP remote-write foundation is deliverable and implemented
- live infra rollout is now blocked only by:
  - deployed runtime emission visibility on public `test` surfaces, and
  - Grafana server-side public embed settings
- accepted rollout path remains:
  1. deploy `test` with `prometheus.enabled=true`
  2. trigger API/snapshot/render flows
  3. verify populated Grafana panels and iframe on `test`

## Additional live verification

- Grafana datasource health for `DTM YMP Test`:
  - endpoint: `GET /api/datasources/uid/effm65zf51xc0b/health`
  - result: `200`, `Successfully queried the Prometheus API.`
- Grafana datasource proxy for metric discovery:
  - endpoint: `GET /api/datasources/proxy/uid/effm65zf51xc0b/api/v1/label/__name__/values`
  - result: `200`
  - confirmed metrics include:
    - `dtm_snapshot_update_duration_ms`
    - `dtm_snapshot_fetch_sheet_ms`
    - `dtm_render_duration_ms`
    - `dtm_render_build_plan_ms`
    - `dtm_api_duration_ms`
    - `dtm_worker_commands_total`
- Grafana dashboard `dtm-test-ops` panels are now explicitly bound to datasource uid:
  - `effm65zf51xc0b`
  - verification via `GET /api/dashboards/uid/dtm-test-ops`
- Grafana query API returns real timeseries from YMP:
  - query: `dtm_snapshot_update_duration_ms{env="test",namespace="dtm",service="dtm"}`
  - result: non-empty `timeseries-multi` frame
- Public iframe path is still blocked by Grafana server config:
  - request: `GET /d/dtm-test-ops/dtm-test-ops?kiosk&theme=light`
  - result: `302 /login`
  - headers include:
    - `X-Frame-Options: deny`
  - implication:
    - datasource/dashboard path is healthy
    - iframe embedding still requires VPS-side Grafana config (`allow_embedding`, anonymous viewer or other embed auth model)

## Public dashboard verification

- externally shared/public dashboard created through Grafana API:
  - dashboard uid: `dtm-test-ops`
  - public dashboard uid: `effmku80r2800d`
- public dashboard endpoints verified:
  - `GET /public-dashboards/af7606b66c8d4ca9b069ea1913577e45`
  - result: `200`
  - no `/login` redirect
- public dashboard token verification:
  - `GET /api/public/dashboards/effmku80r2800d`
  - result: `400 Invalid access token`
  - `GET /api/public/dashboards/af7606b66c8d4ca9b069ea1913577e45`
  - result: `200`
- conclusion:
  - authentication problem is solved without enabling Grafana-wide anonymous access
  - canonical public dashboard URL for `test` is:
    - `http://style-app.solofarm.ru:3000/public-dashboards/af7606b66c8d4ca9b069ea1913577e45`
  - canonical embed URL for `test` is:
    - `http://style-app.solofarm.ru:3000/public-dashboards/af7606b66c8d4ca9b069ea1913577e45?kiosk&theme=light`
- remaining blocker is narrowed to one server-side header/config issue:
  - `X-Frame-Options: deny`
  - required fix on VPS:
    - `[security] allow_embedding = true`
