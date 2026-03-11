# CAM-METRICS-BATCHING-E2E-AND-DASHBOARD-CLEANUP-V1 Evidence

## Trust gate
- source: active observability backends, worker path, snapshot/render jobs, Grafana dashboard spec
- last_verified_at: 2026-03-11
- verified_by: Codex
- trust_level: high

## Verified baseline
- `YandexMonitoringMetricsClient` emits one HTTP write per metric call
- `YandexManagedPrometheusRemoteWriteClient` emits one remote-write request per metric call
- `CompositeMetricsClient` fans out sequentially for each metric call
- snapshot success path emits enough metrics to explain dozens of backend requests in dual-write mode
- Grafana timeseries panels still visually overstate sparse event executions because of range-query rendering defaults

## Execution notes
- source: active observability backends, worker path, update/render jobs, Grafana dashboard spec
- last_verified_at: 2026-03-11
- verified_by: Codex
- evidence:
  - `src/observability/metrics.py`
  - `src/observability/prometheus_metrics.py`
  - `src/observability/composite_metrics.py`
  - `src/observability/batching.py`
  - `src/jobs/update_snapshot_job.py`
  - `src/jobs/render_timeline_job.py`
  - `src/jobs/render_designers_job.py`
  - `src/worker/worker.py`
  - `src/infra/grafana_specs.py`
  - `.venv\\Scripts\\python.exe -m unittest tests.observability.test_yandex_monitoring_metrics tests.observability.test_prometheus_metrics tests.observability.test_metrics_batching tests.infra.test_grafana_specs tests.snapshot_engine.test_update_job tests.snapshot_engine.test_update_job_timings tests.worker.test_retry_semantics tests.api.test_runtime_execution -v`
  - `python -m py_compile src/observability/batching.py src/observability/metrics.py src/observability/prometheus_metrics.py src/observability/composite_metrics.py src/jobs/update_snapshot_job.py src/jobs/render_timeline_job.py src/jobs/render_designers_job.py src/worker/worker.py src/infra/grafana_specs.py`
- trust_level: high
- notes:
  - local code path is coherent: metric writes are batched per operation and flush metrics are explicit
  - live `test` evidence is still required to measure actual wall-clock reduction

## Implemented locally
- `MetricsBatchCollector` added for operation-local buffering and one-shot flush per backend
- Monitoring backend now flushes many points in one `write_metrics(... metrics=[...])`
- YMP backend now flushes many samples in one remote-write payload
- Composite backend now fans out one batch per backend
- snapshot job emits:
  - `dtm.snapshot.job_wall_clock_ms`
  - `dtm.metrics.flush_duration_ms`
  - `dtm.metrics.flush_points_total`
  - `dtm.metrics.flush_failures_total`
- render jobs emit:
  - `dtm.render.job_wall_clock_ms`
  - flush metrics via the same batching path
- worker emits:
  - `dtm.worker.wall_clock_ms`
  - flush metrics after command completion
- `runtime.dev_mode_metrics` added and wired through config/loader
- Grafana spec now:
  - disables point markers on sparse timeseries
  - adds stat panels for `Snapshot Business Duration`, `Snapshot Job Wall Clock`, `Worker Wall Clock`, and `Metrics Flush Total`

## Remaining proof step
- deploy to `test`
- trigger several snapshot updates and render runs
- capture before/after:
  - operator-observed wall-clock
  - `dtm.snapshot.update_duration_ms`
  - `dtm.snapshot.job_wall_clock_ms`
  - `dtm.worker.wall_clock_ms`
  - `dtm.metrics.flush_duration_ms{backend="combined"}`
  - `dtm.metrics.flush_points_total`
