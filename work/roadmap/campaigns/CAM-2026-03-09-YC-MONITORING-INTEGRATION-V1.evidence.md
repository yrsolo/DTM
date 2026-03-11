# CAM-2026-03-09-YC-MONITORING-INTEGRATION-V1 Evidence

## Trust gate

- source: active runtime code, deploy config, local YC CLI session, deployed `test` function, live Monitoring API probes
- last_verified_at: 2026-03-09
- verified_by: Codex
- evidence:
  - `src/observability/metrics.py`
  - `src/app/bootstrap.py`
  - `src/infra/yc_function_info.py`
  - `src/infra/yc_iam.py`
  - `src/infra/yc_monitoring.py`
  - `config/runtime.yaml`
  - `.github/workflows/deploy_yc_function_main.yml`
  - live `GET https://dtm-api-test.solofarm.ru/info?format=json`
  - live `GET https://dtm-api-test.solofarm.ru/api/v2/frontend?limit=1`
  - live `POST /admin/commands/render-timeline`
  - live probe against `POST /monitoring/v2/data/write`
  - live metric listing from `GET /monitoring/v2/metrics`
- trust_level: high
- notes:
  - code baseline is stable and verified
  - custom metrics write endpoint is confirmed live
  - dashboard automation is verified via gRPC DashboardService on `monitoring.api.cloud.yandex.net:443`
  - test contour emits real custom metrics into Yandex Monitoring

## Baseline facts

- current metrics backend default is `NoopMetricsClient`
- active runtime already emits bounded metrics through `MetricsClient`
- folder id is available from deploy config
- current CLI session is authenticated against the target cloud/folder
- current test deploy enables Monitoring via workflow env overrides
- current prod release keeps Monitoring disabled

## Yandex-side evidence

- custom metrics write probe:
  - endpoint: `POST /monitoring/v2/data/write?folderId=<folder>&service=custom`
  - result: HTTP 200
- metric visibility probe:
  - endpoint: `GET /monitoring/v2/metrics?folderId=b1g42qj26s1u7gv7bufm&pageSize=500`
  - result: `dtm.api.*`, `dtm.render.*`, `dtm.worker.*` are visible with `env=test`
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

## Live test smoke

- deployed test function version: `c9078f7`
- `/info?format=json` telemetry block:
  - `metricsEnabled=true`
  - `metricsClient=YandexMonitoringMetricsClient`
  - `monitoringBackend=yandex_monitoring`
  - `monitoringFolderId=b1g42qj26s1u7gv7bufm`
  - `dashboardName=DTM Test Observability`
  - `dashboardId=fbe6m08jl1vj212t5v0c`
- live API request:
  - `GET /api/v2/frontend?limit=1`
  - result: HTTP 200
- live render enqueue:
  - `POST /admin/commands/render-timeline`
  - result: accepted
- live render terminal job:
  - status: `success`
  - monitoring evidence: `dtm.render.total`, `dtm.render.duration_ms`, `dtm.render.rows_rendered`, `dtm.render.cells_written`
- live worker evidence:
  - `dtm.worker.commands_total`
  - `dtm.worker.command_duration_ms`
- live API evidence:
  - `dtm.api.requests_total`
  - `dtm.api.duration_ms`
  - `dtm.api.response_size_bytes`

## Root cause fixed during rollout

- initial test deploy emitted no metrics even with Monitoring enabled
- confirmed causes:
  1. runtime env did not include `YC_SA_JSON_CREDENTIALS`
  2. Monitoring auth needed fallback to attached runtime service account metadata token
  3. custom metrics payload used reserved `service` label and Monitoring silently returned `writtenMetricsCount=0`
- fixes delivered:
  - `src/infra/yc_iam.py` metadata-token fallback
  - `src/infra/yc_monitoring.py` now uses `service_name` label instead of reserved `service`

## Remaining verification / follow-up

- notify enqueue path on test returned unexpected legacy-style body during smoke and is not counted as blocking this CAM
- telegram accepted metric path is not yet proven on live contour in this evidence set
- `/info` build block still has a separate 404 issue in function version lookup and does not block metric ingestion

## Open operational risk

- runtime service account Monitoring write permission is verified for custom metrics ingestion on test
- dashboard creation is verified from local YC session; runtime does not need dashboard mutation rights
- dashboard automation rights for runtime are intentionally not required

## Runtime auth finding

- deployed test function version does not receive `YC_SA_JSON_CREDENTIALS` in runtime env
- this is acceptable after auth fix:
  - runtime now falls back to metadata token from attached service account
  - no secret service-account key needs to be injected into function env for Monitoring/API introspection
