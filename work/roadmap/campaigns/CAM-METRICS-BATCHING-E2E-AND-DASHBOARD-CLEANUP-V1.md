# CAM-METRICS-BATCHING-E2E-AND-DASHBOARD-CLEANUP-V1

## Goal
Убрать пер-metric HTTP emission overhead из active observability path, измерить полный wall-clock для snapshot/worker, и подчистить Grafana dashboard под sparse event metrics.

## Scope
- per-operation metrics batching
- `dtm.metrics.*` flush metrics
- `dtm.snapshot.job_wall_clock_ms`
- `dtm.worker.wall_clock_ms`
- `runtime.dev_mode_metrics`
- Grafana panel cleanup for sparse metrics

## Non-goals
- не меняем бизнес-логику snapshot/render/notify
- не меняем queue semantics
- не добавляем background metrics daemon

## DoD
- snapshot/render/worker emit batched metrics instead of one HTTP call per metric
- flush overhead is directly measurable
- dashboard shows business duration vs worker wall-clock vs flush duration
- detailed metrics are gated by `runtime.dev_mode_metrics`
- focused tests and regression smoke pass before `test` rollout
