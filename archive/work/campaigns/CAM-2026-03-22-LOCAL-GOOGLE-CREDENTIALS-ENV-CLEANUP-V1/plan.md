# CAM-2026-03-22-LOCAL-GOOGLE-CREDENTIALS-ENV-CLEANUP-V1

## Why

The repo still carried a checked-in `key/` fallback for Google service-account credentials even though cloud deploy already reads `GOOGLE_KEY_JSON` from Lockbox.

## Goal

Remove the checked-in key contour and make local/runtime tooling use env-first credential resolution only:
- local: `GOOGLE_KEY_JSON_PATH` or `GOOGLE_KEY_JSON` or `GOOGLE_KEY_JSON_B64`
- cloud: existing Lockbox-provided `GOOGLE_KEY_JSON`

## Trust

- source: current bootstrap code, deploy workflows, local helper scripts, and repo root filesystem
- last_verified_at: 2026-03-22
- verified_by: Codex
- evidence:
  - read `src/platform/bootstrap.py`
  - read `.github/workflows/deploy_yc_function_main.yml`
  - read `.github/workflows/release_yc_function_prod.yml`
  - read `agent/deploy/*.py`
  - read `agent/smokes/cloud_render_freshness_smoke.py`
- trust_level: high
- notes: deploy workflows already used Lockbox; only local fallback and helper defaults needed cleanup

## Tasks

1. Remove checked-in `key/` fallback from bootstrap and helper scripts.
2. Make local/deploy helper tooling use env-first Google credential inputs.
3. Delete the repo `key/` shelf and update docs/examples.
