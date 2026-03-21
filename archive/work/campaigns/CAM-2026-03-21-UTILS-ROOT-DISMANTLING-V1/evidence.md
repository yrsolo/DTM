# CAM-2026-03-21-UTILS-ROOT-DISMANTLING-V1 Evidence

## Trust Gate

- source: current `utils/` contents and active import graph
  - last_verified_at: `2026-03-21`
  - verified_by: `Codex`
  - evidence:
    - `Get-Content utils/func.py`
    - `Get-Content utils/service.py`
    - `Get-Content utils/storage.py`
    - `rg -n "from utils\\.(func|service|storage)|import utils\\.(func|service|storage)|utils\\.(func|service|storage)" src tests agent web_prototype local_run.py`
  - trust_level: `high`
  - notes: `utils/` is not dead legacy; it contains live code used by rendering, Google Sheets adapters, artifact upload helpers, and reminder support. The right move is redistribution into `src/`, not archival as-is.

## Active Tasks

- [x] move active `utils` code into role-true `src/` homes
- [x] rewrite imports and tests
- [x] add guardrails against `utils.*` regressions
- [x] verify targeted contour checks

## Verification

- `rg -n "from utils\\.|import utils\\.|utils\\.(func|service|storage)" src tests agent local_run.py web_prototype work .github -g '!archive/**'`
  - result: no remaining active `utils.*` imports
- `python -m unittest tests.platform.integrations.google_sheets.test_service_dataframe tests.architecture.test_guardrails_v0 tests.api.test_frontend_api_v2_payload tests.core.test_timing_year_modes tests.services.test_readmodel_enums tests.test_task_query_contract tests.contexts.snapshot.test_sheets_normalized_source -v`
  - result: `61 tests, OK`
- `python -m agent.smokes.group_query_smoke`
  - result: `group_query_smoke_ok`
- `python -m agent.prototype.prepare_web_prototype_payload_smoke`
  - result: `prepare_web_prototype_payload_smoke_ok`
- `Test-Path .\\utils -PathType Container`
  - result: `False`

## Verdict

`utils/` was not dead legacy; it was live code in the wrong place. The wave is complete after redistributing that code into `src/`, removing the root `utils/` Python surface, and adding guardrails so the junk-drawer root cannot silently return.
