# DTM-72: TSK-075 Stage 8 static web prototype views and filters over fixture payload

## Context
- Stage 8 loader with schema gate is ready.
- Stage 8 needs visible Spike-1 prototype surfaces for timeline/by-designer/task-details.

## Goal
- Add static web prototype assets and basic filters over fixture payload.

## Non-goals
- No auth, no write-back, no production deployment.

## Plan
1. Add static UI assets (`index.html`, `styles.css`, `app.js`).
2. Add local server helper for preview.
3. Add asset smoke checks.
4. Sync Stage 8 docs and counters.

## Checklist (DoD)
- [x] Three views renderers exist (timeline/by-designer/task-details).
- [x] Designer/status/date filters wired.
- [x] Local preview helper script added.
- [x] Asset smoke passes.
- [x] Sprint/docs aligned (`done 3 / remaining 3`).

## Work log
- 2026-02-27: DTM-72 created and moved to `V rabote`.
- 2026-02-27: Added `web_prototype/static/*`, `agent/run_web_prototype_server.py`, `agent/web_prototype_assets_smoke.py`.
- 2026-02-27: Updated Stage 8 docs/counters and README prototype run hint.

## Links
- Jira: DTM-72
- Stage plan: `doc/19_stage8_execution_plan.md`
