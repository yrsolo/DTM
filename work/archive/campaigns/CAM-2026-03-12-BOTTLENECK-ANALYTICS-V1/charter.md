# CAM-2026-03-12-BOTTLENECK-ANALYTICS-V1 Charter

## Problem
- frontend default read path still sits around `3-5s` on `test`
- current metrics show total latency, masking cost, and response-cache cost, but not where the remaining budget is spent
- detailed diagnostics must stay config-gated so instrumentation itself does not become the new bottleneck

## Goal
- add reusable, config-gated bottleneck analytics with frontend read path as the first active consumer
- expose stage timing evidence through metrics, Grafana, and `/info` diagnostics
- produce live `test` evidence that identifies the dominant remaining latency stage for default frontend requests

## Non-goals
- this campaign does not optimize runtime latency directly
- this campaign does not add universal query caching beyond the already delivered default-response cache
- this campaign does not expand detailed stage analytics to every runtime path in the first increment

## Exit Criteria
- `runtime.bottleneck_metrics_level` supports `off|stages|debug` with backward compatibility for `dev_mode_metrics`
- frontend read path emits `dtm.api.stage.*` metrics for the agreed stage breakdown
- Grafana dashboard contains frontend bottleneck panels
- `/info` detail shows current profiling level and recent stage traces
- live `test` evidence identifies the dominant frontend latency stage for the default query
