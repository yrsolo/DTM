# DTM-73: TSK-076 Stage 8 local/cloud source switch wiring for prototype consumer

## Context
- Stage 8 loader and static prototype are already in place.
- Prototype needs explicit source switching (`filesystem`/`object_storage`) and auto mode for environment-driven runs.

## Goal
- Add payload preparation helper with `auto/filesystem/object_storage` source-mode.
- Wire UI to auto-load prepared payload when available.

## Non-goals
- No production runtime path changes.
- No frontend framework migration.

## Plan
1. Add payload preparation CLI with source-mode resolution.
2. Add UI autoload hook for `prototype_payload.json`.
3. Add smoke check for filesystem mode path.
4. Sync Stage 8 docs and counters.

## Checklist (DoD)
- [x] `prepare_web_prototype_payload.py` added.
- [x] Source switch supports `auto/filesystem/object_storage`.
- [x] UI autoload path is wired.
- [x] Smoke checks pass.
- [x] Sprint/docs updated (`done 4 / remaining 2`).

## Work log
- 2026-02-27: DTM-73 created and moved to `V rabote`.
- 2026-02-27: Added `agent/prepare_web_prototype_payload.py` and `agent/prepare_web_prototype_payload_smoke.py`.
- 2026-02-27: Updated `web_prototype/static/app.js` with auto-load of `prototype_payload.json`.
- 2026-02-27: Synced Stage 8 docs and counters.

## Links
- Jira: DTM-73
- Stage plan: `doc/19_stage8_execution_plan.md`
