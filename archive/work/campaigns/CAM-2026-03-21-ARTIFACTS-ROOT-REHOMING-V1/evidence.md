# CAM-2026-03-21-ARTIFACTS-ROOT-REHOMING-V1 Evidence

## Trust Gate

- source: current references to root `artifacts/` across runtime, tooling, tests, and workflows
  - last_verified_at: `2026-03-21`
  - verified_by: `Codex`
  - evidence:
    - `rg -n --fixed-strings "artifacts/" src agent tests scripts .github README.md docs work local_run.py index.py`
    - `Get-ChildItem -Force artifacts -Recurse`
    - `Get-Content src/platform/bootstrap.py`
  - trust_level: `high`
  - notes: root `artifacts/` no longer serves as a code home; it is a generated-output shelf plus one bootstrap fallback path. The correct move is to rehome outputs under `work/`, not archive the active artifact scripts.

## Active Tasks

- [x] rewrite active defaults to `work/artifacts/`
- [x] update tests and workflow excludes
- [x] migrate existing local output files into `work/artifacts/`
- [x] remove the root `artifacts/` directory and verify targeted contour checks

## Verification

- `python -m unittest tests.platform.test_bootstrap_inputs tests.platform.infra.test_operational_store tests.architecture.test_guardrails_v0 tests.entrypoints.test_import_safety tests.platform.integrations.google_sheets.test_service_dataframe -v`
  - result: `57 tests, OK`
- `rg -n --fixed-strings "artifacts/" src agent tests scripts .github README.md docs work local_run.py index.py`
  - result: active code/workflows now point to `work/artifacts/`; remaining root-artifacts mentions survive only in historical work artifacts
- `if (Test-Path -LiteralPath '.\\artifacts') { 'ROOT_ARTIFACTS_ACTIVE' } else { 'ROOT_ARTIFACTS_REMOVED' }`
  - result: `ROOT_ARTIFACTS_REMOVED`

## Verdict

Root `artifacts/` was an accidental output shelf, not an intentional repo root. Outputs now live under `work/artifacts/`, artifact scripts remain active in `agent.artifacts`, and the repo root no longer carries generated local evidence.
