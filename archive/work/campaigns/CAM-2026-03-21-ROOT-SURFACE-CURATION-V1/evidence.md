# CAM-2026-03-21-ROOT-SURFACE-CURATION-V1 Evidence

## Trust Gate

- source: current repo-root directory map and live import graph
  - last_verified_at: `2026-03-21`
  - verified_by: `Codex`
  - evidence:
    - `Get-ChildItem -Force`
    - `Get-ChildItem -Force web_prototype -Recurse`
    - `Get-ChildItem -Force artifacts -Recurse`
    - `rg -n "from web_prototype\\.|import web_prototype\\.|artifacts/|artifacts\\\\" src tests agent scripts .github README.md docs work local_run.py index.py`
    - `if (Test-Path .\\core -PathType Container) { Get-ChildItem -Force .\\core }`
  - trust_level: `high`
  - notes: `web_prototype/` and `artifacts/` are still live roots, but they are special-purpose support/output surfaces rather than misplaced runtime code. The real dead root was the leftover physical `core/` directory after tracked code moved to `src/core/`.

## Verification

- `if (Test-Path -LiteralPath '.\\core') { 'ROOT_CORE_EXISTS' } else { 'ROOT_CORE_MISSING' }`
  - result: `ROOT_CORE_MISSING`
- `if (Test-Path -LiteralPath '.\\__pycache__') { 'ROOT_PYCACHE_EXISTS' } else { 'ROOT_PYCACHE_MISSING' }`
  - result: `ROOT_PYCACHE_MISSING`
- `if (Test-Path -LiteralPath '.\\web_prototype\\__pycache__') { 'WEB_PROTO_PYCACHE_EXISTS' } else { 'WEB_PROTO_PYCACHE_MISSING' }`
  - result: `WEB_PROTO_PYCACHE_MISSING`
- `python -m unittest tests.architecture.test_guardrails_v0 tests.entrypoints.test_import_safety tests.platform.integrations.google_sheets.test_service_dataframe tests.api.test_frontend_api_v2_payload -v`
  - result: `53 tests, OK`

## Verdict

Repo-root curation should prefer truthful special-purpose roots over forced relocation. `artifacts/` and `web_prototype/` stay at the top level with explicit READMEs; dead physical leftovers such as the old root `core/` and repo `__pycache__/` should disappear.
