# Active Tasks

- CAM-UNIFIED-API-INGRESS-V1 P01: switch repo/operator URLs to path-based `/test` and `/prod` base paths and add unified API gateway rollout script
- CAM-UNIFIED-API-INGRESS-V1 P02: create unified Yandex API Gateway on `dtm.solofarm.ru` for `/test/*` and `/prod/*`, replace Yandex DNS `dtm.solofarm.ru` CNAME to the new gateway, and keep old `dtm-api-*` domains as rollback paths during propagation
- CAM-GRAFANA-PROM-OPS-DASHBOARD-V1 P01: register campaign, trust gate, and typed `prometheus`/`grafana` config for dual-write and iframe metadata
- CAM-GRAFANA-PROM-OPS-DASHBOARD-V1 P02: add Prometheus metrics backend, composite dual-write client, and additive `/info` Grafana/Prometheus telemetry fields
- CAM-GRAFANA-PROM-OPS-DASHBOARD-V1 P03: add Grafana dashboard spec/API helpers and record infra blockers for Yandex Prometheus workspace discovery and VPS SSH access
- CAM-GRAFANA-PROM-OPS-DASHBOARD-V1 P04: replace generic Prometheus text push with real Yandex Managed Prometheus remote write and keep remaining blocker limited to workspace/API key + datasource rollout
- CAM-GRAFANA-PROM-OPS-DASHBOARD-V1 P05: add self-service workspace/datasource runbook and one-command Grafana datasource provisioning from repo
- CAM-GRAFANA-PROM-OPS-DASHBOARD-V1 P06: record shared YMP workspace id, create Grafana datasource `DTM YMP Test`, and switch remaining blocker to live sample emission only

## Notes

- `CAM-2026-03-10-DATALENS-OPS-DASHBOARD-V1`: workbook and Monitoring connection are provisioned; `createQLChart` is currently blocked by live DataLens API `500 Access service error` on the Monitoring connection.
- `CAM-2026-03-10-DATALENS-OPS-DASHBOARD-V1`: caller permissions were raised for `yrsolo` (`viewer` + `monitoring.viewer`) and the same `createQLChart` error persists, so the blocker is now classified as external to repo code.
- `CAM-GRAFANA-PROM-OPS-DASHBOARD-V1`: repo-side dual-write/Grafana foundation is being added first; active code path now uses real Yandex Managed Prometheus remote write and the remaining blocker is external infra only: workspace/API key + Grafana datasource endpoint wiring.
- `CAM-GRAFANA-PROM-OPS-DASHBOARD-V1`: Grafana API token path is proven; folder `DTM Test` and dashboard `dtm-test-ops` are created on `https://grafana.solofarm.ru`, and datasource wiring is proven against YMP.
- `CAM-GRAFANA-PROM-OPS-DASHBOARD-V1`: before datasource rollout, the repo must stop pretending that text exposition push is YMP-compatible; current execution slice replaces it with actual remote write semantics.
- `CAM-GRAFANA-PROM-OPS-DASHBOARD-V1`: workspace creation remains a UI-only Yandex-side step; repo now provides `scripts/provision_grafana_datasource.py` so the only missing operator input is the final `workspace_id`.
- `CAM-GRAFANA-PROM-OPS-DASHBOARD-V1`: shared workspace `mon73oiiclfbmmqbjejn` is now known and Grafana datasource `DTM YMP Test` is created; the next blocker is only live sample emission from deployed test runtime.
- `CAM-GRAFANA-PROM-OPS-DASHBOARD-V1`: Grafana datasource query path is now proven against YMP and imported dashboard panels are bound to datasource uid `effm65zf51xc0b`.
- `CAM-GRAFANA-PROM-OPS-DASHBOARD-V1`: public dashboard `effmku80r2800d` is created and works without login; the remaining blocker for webpage embed is only Grafana server-side `allow_embedding = true` because current responses still send `X-Frame-Options: deny`.
- `CAM-GRAFANA-PROM-OPS-DASHBOARD-V1`: public dashboard panel failures were caused by missing `refId` fields in multi-query panels; dashboard spec now assigns explicit `A..E` refIds and the public dashboard JSON is valid again.

## Done

- CAM-SNAPSHOT-PREP-BULK-REFORM-V1 P01: register trust gate, add prep-build sub-metrics, and switch snapshot builder contract to timing-aware bulk-extra path
- CAM-SNAPSHOT-PREP-BULK-REFORM-V1 P02: replace per-task S3 extra layout with one bulk extra snapshot and remove orphan N+1 writes from hot path
- CAM-SNAPSHOT-PREP-BULK-REFORM-V1 P03: add one-time migration script, update attachment mutation flow, migrate/verify `test`, and prove live `build_prep_ms` drop without public contract drift

- CAM-2026-03-10-DATALENS-OPS-DASHBOARD-V1 P01: register DataLens dashboard campaign, typed config, API/spec modules, and additive `/info` metadata
- CAM-2026-03-10-DATALENS-OPS-DASHBOARD-V1 P02: provision DataLens workbook/Monitoring connection and exhaust caller-permission hypothesis for `createQLChart`
- CAM-SNAPSHOT-RENDER-TIMINGS-V1 P01: add detailed snapshot timings for fetch/normalize/build_prep/write_raw/write_prep and surface them through metrics and job result
- CAM-SNAPSHOT-RENDER-TIMINGS-V1 P02: add detailed render timings for build_plan/write_sheet/total and surface them through metrics and job result

- CAM-2026-03-09-QUEUE-RETRY-SEMANTICS-V1 P01: extend worker result/status vocabulary to retryable vs terminal failures
- CAM-2026-03-09-QUEUE-RETRY-SEMANTICS-V1 P02: update dispatcher/worker/worker-shell semantics and add retry-focused tests
- CAM-2026-03-09-GREP-GATES-V1 P01: extend forbidden-import guard to telegram/commands/worker/observability scopes
- CAM-2026-03-09-GREP-GATES-V1 P02: wire legacy guard scripts into test/prod deploy workflows
- CAM-2026-03-09-OBSERVABILITY-FOUNDATION-V1 P01: add shared observability modules for metrics, timing, and structured logging
- CAM-2026-03-09-OBSERVABILITY-FOUNDATION-V1 P02: instrument snapshot/render/notify/http boundaries and expose additive telemetry info in `/info`
- CAM-2026-03-09-TELEGRAM-COMMAND-ROUTER-V1 P01: add typed Telegram DTOs and dedicated command router
- CAM-2026-03-09-TELEGRAM-COMMAND-ROUTER-V1 P02: keep webhook enqueue-only while splitting parser and router responsibilities
- CAM-2026-03-09-TELEGRAM-COMMAND-ROUTER-V1 P03: add parser/router tests and align docs/tracking with current post-legacy baseline
- CAM-2026-03-09-YC-MONITORING-INTEGRATION-V1 P01: add typed monitoring config, YC IAM helper, and real Yandex Monitoring metrics client
- CAM-2026-03-09-YC-MONITORING-INTEGRATION-V1 P02: wire monitoring backend in bootstrap, add docs, and create/update test Yandex Monitoring dashboard
- CAM-2026-03-09-YC-MONITORING-INTEGRATION-V1 P03: deploy monitoring-enabled test contour and capture live metric emission evidence from `/info`, API, and render on the real test function

## Notes

- `CAM-2026-03-09-RUNTIME-DEPLANNERIZE-V1` is not opened as active work because the runtime is already post-deplannerization after the legacy-cut sequence.
- Monitoring integration is considered complete for test-first scope; notify enqueue inconsistency and `/info` build 404 remain separate follow-up issues.
