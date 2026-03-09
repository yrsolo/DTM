# CAM-2026-03-09-YC-MONITORING-INTEGRATION-V1 Evidence

## Trust gate

- source: active runtime code, deploy config, local YC CLI session
- last_verified_at: 2026-03-09
- verified_by: Codex
- evidence:
  - `src/observability/metrics.py`
  - `src/app/bootstrap.py`
  - `src/infra/yc_function_info.py`
  - `config/runtime.yaml`
  - `config/deploy.yaml`
  - `yc config list`
  - live probe against `POST /monitoring/v2/data/write`
- trust_level: medium
- notes:
  - code baseline is stable and verified
  - custom metrics write endpoint is confirmed live
  - dashboard automation is verified via gRPC DashboardService on `monitoring.api.cloud.yandex.net:443`

## Baseline facts

- current metrics backend default is `NoopMetricsClient`
- active runtime already emits bounded metrics through `MetricsClient`
- folder id is available from deploy config
- current CLI session is authenticated against the target cloud/folder

## Yandex-side evidence

- custom metrics write probe:
  - endpoint: `POST /monitoring/v2/data/write?folderId=<folder>&service=custom`
  - result: HTTP 200
- dashboard API probe:
  - gRPC service: `yandex.cloud.monitoring.v3.DashboardService`
  - endpoint: `monitoring.api.cloud.yandex.net:443`
  - `List` works with IAM token from current `yc` session
  - test dashboard created and updated successfully
- test dashboard:
  - id: `fbe6m08jl1vj212t5v0c`
  - name: `dtm-test-observability`
  - title: `DTM Test Observability`
  - widgets: 6

## Remaining verification

- deployed test function still needs smoke after rollout:
  - `/info?format=json` telemetry block
  - API metric emission
  - render metric emission
  - notify metric emission
  - telegram accepted metric emission

## Open operational risk

- runtime service account Monitoring write permission is still unverified until deployed test emits live metrics
- dashboard creation is verified from local YC session; runtime does not need dashboard mutation rights
