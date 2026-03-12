# Metrics Schema

## Required labels

- `env`
- `module`
- `operation`
- `result`

## Naming rules

- counters: `*_total`
- timings: `*_duration_ms` or specific `*_ms`
- gauges: `*_current`, `*_seconds`, or domain-specific current value names

## Groups

### Snapshot

- `dtm.snapshot.update_total`
- `dtm.snapshot.update_duration_ms`
- `dtm.snapshot.job_wall_clock_ms`
- `dtm.snapshot.fetch_sheet_ms`
- `dtm.snapshot.normalize_ms`
- `dtm.snapshot.build_prep_ms`
- `dtm.snapshot.extra_load_ms`
- `dtm.snapshot.orphan_reconcile_ms`
- `dtm.snapshot.task_view_build_ms`
- `dtm.snapshot.prep_index_build_ms`
- `dtm.snapshot.write_raw_ms`
- `dtm.snapshot.write_prep_ms`
- `dtm.snapshot.changed_total`
- `dtm.snapshot.nochange_total`

### API

- `dtm.api.requests_total`
- `dtm.api.duration_ms`
- `dtm.api.masking_ms`
- `dtm.api.response_size_bytes`
- `dtm.api.response_cache.hit_total`
- `dtm.api.response_cache.miss_total`
- `dtm.api.response_cache.write_total`
- `dtm.api.response_cache.read_ms`
- `dtm.api.response_cache.write_ms`
- `dtm.api.prep_age_seconds`

### Info

- `dtm.info.summary.ms`
- `dtm.info.detail.ms`

### Render

- `dtm.render.total`
- `dtm.render.duration_ms`
- `dtm.render.job_wall_clock_ms`
- `dtm.render.build_plan_ms`
- `dtm.render.write_sheet_ms`
- `dtm.render.rows_rendered`
- `dtm.render.cells_written`

### Notify

- `dtm.notify.total`
- `dtm.notify.duration_ms`
- `dtm.notify.selection_ms`
- `dtm.notify.formatting_ms`
- `dtm.notify.send_ms`
- `dtm.notify.messages_sent`
- `dtm.notify.tasks_selected`

### Telegram

- `dtm.telegram.updates_total`
- `dtm.telegram.accepted_total`
- `dtm.telegram.rejected_total`
- `dtm.telegram.enqueue_ms`
- `dtm.telegram.command_total`

### Worker / Queue

- `dtm.worker.commands_total`
- `dtm.worker.command_duration_ms`
- `dtm.worker.wall_clock_ms`
- `dtm.worker.command_failures_total`
- `dtm.worker.command_retries_total`
- `dtm.worker.dlq_total`

### Metrics Flush

- `dtm.metrics.flush_duration_ms`
- `dtm.metrics.flush_points_total`
- `dtm.metrics.flush_failures_total`

## Current implementation notes

`src/observability/*` is the shared abstraction layer for metrics and timing wrappers.

Snapshot runtime notes:

- `fetch_sheet_ms` now covers one values read plus one canonical `A`-column color read only.
- `normalize_ms` no longer includes a second Google color fetch.
- `job_wall_clock_ms` captures full snapshot job wall-clock including metric flush overhead.
- detailed snapshot substage metrics are gated by `runtime.dev_mode_metrics`.
- Grafana derives `last` and `avg5` operator stats from raw metrics at dashboard level; runtime no longer emits presentation-only `*_last_ms` / `*_last5_avg_ms` gauges.

Metrics batching notes:

- active jobs now batch metrics per operation and flush once per backend instead of one HTTP request per metric point
- `dtm.metrics.flush_duration_ms` and `dtm.metrics.flush_points_total` measure backend flush cost directly
- `dtm.worker.wall_clock_ms` captures worker-side wall-clock including status-store writes and metric flush
- `/info` summary/detail timing is emitted separately so default operator reads can be compared against heavy diagnostics explicitly
- browser-facing masked mode emits `dtm.api.masking_ms` so masking overhead stays measurable without forking the canonical query path
- exact default frontend query may now use Object Storage response cache for `full` and `masked` variants; cache read/write path emits dedicated `dtm.api.response_cache.*` metrics

Current runtime default:

- `NoopMetricsClient`

This keeps instrumentation points stable even before a real Yandex Monitoring adapter is wired in production.
