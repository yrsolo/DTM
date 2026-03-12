# CAM-GRAFANA-RAW-AGG-STATS-V1

## Goal
- move Grafana operator stat panels from runtime-derived gauges to raw-metric aggregation
- keep raw snapshot/render stage metrics as the only canonical source of truth
- avoid presentation-only metric multiplication in runtime

## Scope
- `last` values are derived in Grafana from raw metrics via `last_over_time(...)`
- exact `avg5` values are derived in Grafana through panel transformations over raw metric series
- runtime snapshot/render jobs stop emitting `*_last_ms` / `*_last5_avg_ms`
- Grafana spec is updated and reprovisioned with the same dashboard UID

## Non-goals
- no public API changes
- no snapshot/render algorithm changes
- no Monitoring/YMP topology changes

## Status
- implemented in code
- pending focused verification in Grafana live dashboard
