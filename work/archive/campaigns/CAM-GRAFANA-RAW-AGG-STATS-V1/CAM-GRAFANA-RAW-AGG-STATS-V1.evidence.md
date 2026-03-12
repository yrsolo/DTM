# CAM-GRAFANA-RAW-AGG-STATS-V1 Evidence

## Trust gate
- source: active Grafana spec, snapshot/render jobs, metrics docs
- last_verified_at: 2026-03-11
- verified_by: Codex
- trust_level: high

## Verified implementation
- `src/infra/grafana_specs.py` stat panels now use raw metrics only
- current values use `last_over_time(...[7d])`
- avg5 values are derived through Grafana panel transformations over raw series
- snapshot/render jobs no longer emit presentation-only `*_last_ms` / `*_last5_avg_ms`
- metrics docs now describe dashboard-side aggregation as the supported model

## Evidence
- removed runtime imports/usages of:
  - `emit_last_and_avg5_gauges`
  - `extract_recent_success_values`
  - `src/observability/rolling_metrics.py`
- updated focused tests:
  - `tests/infra/test_grafana_specs.py`

## Notes
- live dashboard reprovision and visual verification on Grafana remains the final step for this CAM
