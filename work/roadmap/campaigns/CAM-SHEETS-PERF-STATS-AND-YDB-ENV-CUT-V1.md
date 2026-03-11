# CAM-SHEETS-PERF-STATS-AND-YDB-ENV-CUT-V1

## Goal
- reduce active snapshot fetch/normalize overhead
- add operator-friendly last/avg5 timing stats for snapshot and render in Grafana
- remove YDB from active env/deploy/runtime contour

## Scope
- Sheets fetch path reads only worksheet values plus canonical `A`-column colors
- normalize path consumes snapshot-carried colors and avoids extra Google API calls
- active snapshot runtime path stops using DataFrame-heavy repository conversion
- Grafana spec gains stat panels derived from raw snapshot/render stage metrics
- active workflows/loader/bootstrap stop depending on `YDB_*` env secrets

## Non-goals
- delete YDB adapters or legacy/reference tests
- redesign render algorithm
- change public API payloads

## Status
- implemented in code
- verified by focused unit/smoke tests
- ready for `test` rollout and live metric verification
