# Stage 23 Test Contour Operational Evidence Bundle

## Scope
- Consolidate test-contour evidence for Stage 23 before final closeout.
- Provide explicit production go/no-go input set from executable artifacts.

## Inputs
- Cloud tri-block smoke artifact:
  - `artifacts/tmp/stage23_canary_precheck.json`
- Bundle builder:
  - `agent/stage23_operational_evidence_bundle.py`
- Bundle output:
  - `artifacts/tmp/stage23_operational_evidence_bundle.json`

## Execution Commands
1. Generate smoke input:
   - `.venv\Scripts\python.exe agent\stage23_cloud_tri_block_smoke.py --function-url https://functions.yandexcloud.net/d4e81vgi5vri8poe7qba --api-base https://dtm-api-test.solofarm.ru --timeout 180 --output-file artifacts/tmp/stage23_canary_precheck.json`
2. Build operational bundle:
   - `.venv\Scripts\python.exe agent\stage23_operational_evidence_bundle.py --smoke-file artifacts/tmp/stage23_canary_precheck.json --output-file artifacts/tmp/stage23_operational_evidence_bundle.json`

## Current Test-Contour Result
- `go_no_go_input_ready=true`
- `verdict=ready`
- Required checks: all passed.
- Optional warning:
  - `v2_readmodel_source_present` (field currently empty in cloud payload; non-blocking for readiness package, but keep visible for Stage 24 hardening).

## Production Go/No-Go Input Set
- Required:
  - cloud smoke `ok=true`,
  - sync invoke `200`,
  - API v1 and API v2 `200`,
  - positive task overlap between v1 and v2,
  - v2 contract version present.
- Advisory:
  - `meta.readmodelSource` in v2 payload should be non-empty.

## Decision Note
- Stage 23 can proceed to closeout package with this evidence set.
- Final production switch decision remains owner-controlled and must follow:
  - `doc/ops/stage23_source_policy_canary_rollout_checklist.md`

