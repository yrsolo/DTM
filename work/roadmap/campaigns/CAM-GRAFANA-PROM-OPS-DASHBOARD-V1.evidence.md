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
- live infra rollout is now blocked only by deployed runtime emission on `test`, not by datasource/workspace discovery
- accepted rollout path remains:
  1. deploy `test` with `prometheus.enabled=true`
  2. trigger API/snapshot/render flows
  3. verify populated Grafana panels and iframe on `test`
