# DTM-202: Stage 21 runtime trigger gate and release preflight hotfix

## Context
- Any random HTTP/API call was able to pass through runtime entrypoint and start planner flow.
- Manual PROD release workflow failed on missing repository variable `SOURCE_SHEET_NAME` even though this key is stored in Lockbox.

## Goal
- Allow planner redraw execution only when:
  - cloud trigger id is explicitly mapped in `config.constants.TRIGGERS`, or
  - caller explicitly sets allowed `mode` in function request.
- Remove release dependency on repo-level `SOURCE_SHEET_NAME` and read this key from Lockbox in both deploy workflows.

## Non-goals
- No change to planner business logic.
- No change to API payload contract endpoints.

## Plan
1. Harden `index.py` trigger-mode resolution via `TRIGGERS`.
2. Keep HTTP no-op path for requests without explicit mode.
3. Align deploy workflows to consume `SOURCE_SHEET_NAME` from Lockbox secret mapping.
4. Run smoke checks.

## Checklist (DoD)
- [x] Unknown trigger payload does not launch planner flow.
- [x] Known trigger payload resolves mode from `TRIGGERS`.
- [x] HTTP request without mode returns no-op.
- [x] `SOURCE_SHEET_NAME` removed from workflow preflight repository-variable dependency.
- [x] `SOURCE_SHEET_NAME` is injected via Lockbox in test/prod deploy workflows.
- [x] Local smoke check passed.

## Work log
- 2026-03-02: Updated `index.py` to resolve trigger mode strictly from `TRIGGERS` and run planner only for known triggers or explicit mode.
- 2026-03-02: Updated `.github/workflows/release_yc_function_prod.yml` to map `SOURCE_SHEET_NAME` from Lockbox; removed brittle repo-variable preflight dependency.
- 2026-03-02: Updated `.github/workflows/deploy_yc_function_main.yml` to read `SOURCE_SHEET_NAME` from Lockbox as well.
- 2026-03-02: Smoke check `python -m compileall index.py` passed.

## Links
- `.github/workflows/release_yc_function_prod.yml`
- `.github/workflows/deploy_yc_function_main.yml`
- `index.py`
