# DTM-169: Stage 15 live render freshness smoke

## Context
- Minimal acceptance criterion: corner timestamp should be close to current time.

## Goal
- Validate real render freshness using sheet corner timestamp threshold.

## Non-goals
- Full semantic validation of diagram content.

## Plan
1. Invoke cloud function in timer mode.
2. Read `A1` from target worksheet.
3. Parse timestamp and compare age against threshold.

## Checklist (DoD)
- [x] Freshness parser supports expected timestamp format.
- [x] Threshold-based pass/fail is implemented.
- [x] Live evidence captured (`corner_age_minutes` near now).

## Work log
- 2026-02-28: Live run passed with `corner_age_minutes=0.8` and `cloud_render_freshness_smoke_ok`.

## Links
- `agent/cloud_render_freshness_smoke.py`
- `doc/stages/44_stage15_deploy_readiness_and_render_freshness_guard.md`