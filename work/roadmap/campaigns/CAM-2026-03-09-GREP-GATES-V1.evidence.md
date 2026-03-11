# CAM-2026-03-09-GREP-GATES-V1 Evidence

## Trust gate

- source: active guard scripts and deploy workflows
- last_verified_at: 2026-03-09
- verified_by: Codex
- evidence:
  - `scripts/check_no_legacy_imports.py`
  - `scripts/check_no_legacy_entrypoint_imports.py`
  - `.github/workflows/deploy_yc_function_main.yml`
  - `.github/workflows/release_yc_function_prod.yml`
- trust_level: high

## Delivered

- expanded forbidden-import scope to `src/telegram`, `src/commands`, `src/worker`, `src/observability`
- added `src.legacy` and `src.adapters.store_ydb` to forbidden imports for the new contour
- deploy/release workflows now run both legacy guard scripts
