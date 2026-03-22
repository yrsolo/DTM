# CAM-2026-03-22-LOCAL-GOOGLE-CREDENTIALS-ENV-CLEANUP-V1 - Evidence

## Trust Gate

- source: current bootstrap code, workflows, helper scripts, and root filesystem state
- last_verified_at: 2026-03-22
- verified_by: Codex
- evidence:
  - read `src/platform/bootstrap.py`
  - read `.github/workflows/deploy_yc_function_main.yml`
  - read `.github/workflows/release_yc_function_prod.yml`
  - read `agent/deploy/prepare_prod_release.py`
  - read `agent/deploy/sync_lockbox_from_env.py`
  - read `agent/smokes/cloud_render_freshness_smoke.py`
- trust_level: high
- notes: cloud deploy was already Lockbox-backed before this wave

## Execution Notes

- started: 2026-03-22
- completed: 2026-03-22
- scope: bootstrap/tooling/docs/root-surface cleanup
- updated:
  - `src/platform/bootstrap.py`
  - `agent/smokes/cloud_render_freshness_smoke.py`
  - `agent/deploy/prepare_prod_release.py`
  - `agent/deploy/sync_lockbox_from_env.py`
  - `tests/platform/test_bootstrap_inputs.py`
  - `.env.example`
  - `docs/reference/configuration.md`
- removed:
  - checked-in Google credential file under the root `key/` shelf
  - root `key/` directory itself
- verification:
  - `python -m unittest tests.platform.test_bootstrap_inputs tests.entrypoints.test_import_safety -v`
  - `python -m agent.deploy.sync_lockbox_from_env --dry-run`
  - grep over active repo for old checked-in key fallback references
  - `Test-Path key`
- result:
  - cloud deploy remains Lockbox-backed through `GOOGLE_KEY_JSON`
  - local runtime/tooling is now env-first only
  - no checked-in Google key shelf remains in the repo surface
