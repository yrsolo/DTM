# CAM-2026-03-12-BOTTLENECK-ANALYTICS-V1 Plan

## Phases

### P01 - Config-gated profiling policy
- `CAM-2026-03-12-BOTTLENECK-ANALYTICS-V1-P01-T001` add `runtime.bottleneck_metrics_level` with `off|stages|debug`
- `CAM-2026-03-12-BOTTLENECK-ANALYTICS-V1-P01-T002` keep backward compatibility: `dev_mode_metrics=true` behaves like `stages`

### P02 - Frontend stage instrumentation
- `CAM-2026-03-12-BOTTLENECK-ANALYTICS-V1-P02-T001` emit `dtm.api.stage.duration_ms`, `dtm.api.stage.total`, `dtm.api.stage.failures_total`
- `CAM-2026-03-12-BOTTLENECK-ANALYTICS-V1-P02-T002` instrument frontend read path stages and attach `route`, `access_mode`, `cache_result`
- `CAM-2026-03-12-BOTTLENECK-ANALYTICS-V1-P02-T003` keep recent in-process stage traces for operator diagnostics

### P03 - Surfaces and evidence
- `CAM-2026-03-12-BOTTLENECK-ANALYTICS-V1-P03-T001` expose profiling level and recent traces in `/info` detail
- `CAM-2026-03-12-BOTTLENECK-ANALYTICS-V1-P03-T002` add frontend bottleneck panels to Grafana spec
- `CAM-2026-03-12-BOTTLENECK-ANALYTICS-V1-P03-T003` deploy to `test`, run live measurements, and record dominant stage evidence
