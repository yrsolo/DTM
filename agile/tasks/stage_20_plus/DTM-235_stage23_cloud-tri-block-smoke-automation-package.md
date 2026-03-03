# DTM-235: Stage 23 cloud tri-block smoke automation package

## Context
- Stage 23 requires repeatable cloud evidence for three blocks from Stage 22 unified baseline.
- Existing cloud smoke script (`cloud_smoke_db_migration_v2.py`) validates sync + API v2 only.

## Goal
- Add one cloud smoke script that:
  - triggers sync refresh on function URL,
  - checks API v1 and API v2 endpoints,
  - validates task-id overlap parity and writes machine-readable evidence JSON.

## Non-goals
- No production switch changes.
- No API payload contract changes.

## Plan
1. Add Stage 23 cloud smoke script with evidence file output.
2. Add helper unit tests for deterministic parsing logic.
3. Run cloud smoke against test contour and store evidence artifact.
4. Update README command reference.

## Checklist (DoD)
- [x] `agent/stage23_cloud_tri_block_smoke.py` added.
- [x] Unit tests for helper extraction added.
- [x] Test contour cloud smoke executed successfully.
- [x] Evidence JSON artifact generated (`artifacts/tmp/stage23_cloud_tri_block_smoke.json`).
- [x] README updated with command.

## Work log
- 2026-03-03: Added cloud smoke script with sync invoke + API v1/v2 parity evidence output.
- 2026-03-03: Added `tests/agent/test_stage23_cloud_tri_block_smoke.py`.
- 2026-03-03: Validation passed:
  - `.venv\\Scripts\\python.exe -m unittest tests.agent.test_stage23_cloud_tri_block_smoke tests.api.test_frontend_api_routing -v`
  - `.venv\\Scripts\\python.exe agent\\stage23_cloud_tri_block_smoke.py --function-url https://functions.yandexcloud.net/d4e81vgi5vri8poe7qba --api-base https://dtm-api-test.solofarm.ru --output-file artifacts/tmp/stage23_cloud_tri_block_smoke.json`

## Links
- Script: `agent/stage23_cloud_tri_block_smoke.py`
- Evidence: `artifacts/tmp/stage23_cloud_tri_block_smoke.json`
