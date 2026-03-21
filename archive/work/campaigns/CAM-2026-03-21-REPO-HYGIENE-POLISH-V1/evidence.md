# CAM-2026-03-21-REPO-HYGIENE-POLISH-V1 Evidence

## Trust Gate

- source: current repo root, active `src` tree, tracked helper scripts, active docs, and `agent/`
  - last_verified_at: `2026-03-21`
  - verified_by: `Codex`
  - evidence:
    - `Get-ChildItem -Force`
    - `Get-ChildItem src -Directory`
    - `Get-ChildItem agent -Force`
    - `Get-ChildItem src/app,src/adapters,src/archive,src/commands,src/entrypoint,src/infra,src/observability,src/services,src/worker -Recurse -File`
    - `rg -n "src/(entrypoint|app|infra|observability|worker|commands|adapters|services)/|src\\.(entrypoint|app|infra|observability|worker|commands|adapters|services)" README.md docs work scripts`
  - trust_level: `high`
  - notes: current inspection shows the active architecture map is mostly clean, but helper docs/scripts still mention removed roots and several local-only `__pycache__` shells still make old roots look alive.

## Iteration Notes

- added repo navigation docs:
  - `agent/README.md`
  - `agent/intructions/README.md`
- rewrote `docs/README.md` into a clean docs map and aligned root `README.md` with the actual top path `src/entrypoints/root/handler.py`
- updated active docs that still pointed to removed roots:
  - `src/app/bootstrap.py` -> `src/platform/bootstrap.py`
  - `src/entrypoint/*` -> `src/entrypoints/root/*`
  - `src/worker/*` -> `src/platform/runtime/worker/*`
  - `src/commands/*` -> `src/platform/runtime/commands/*`
  - `src/infra/*` -> `src/platform/integrations/*`
  - `src/observability/*` -> `src/platform/observability/*`
  - `src/services/sources/*` -> `src/contexts/snapshot/adapters/sources/*`
  - `src/services/access/masking.py` -> `src/contexts/access_api/internal/masking.py`
- updated helper scripts to current imports:
  - `scripts/provision_grafana_dashboard.py`
  - `scripts/provision_grafana_datasource.py`
  - `scripts/provision_datalens_dashboard.py`
  - `scripts/render_grafana_dashboard.py`
  - `scripts/check_no_legacy_entrypoint_imports.py`
- moved one historical migration helper out of active `scripts/`:
  - `scripts/migrate_extra_store_to_bulk.py` -> `archive/code/scripts/migrate_extra_store_to_bulk.py`
- removed stale local-only shells after the architecture refactor:
  - empty `src/app`, `src/adapters`, `src/archive`, `src/commands`, `src/entrypoint`, `src/infra`, `src/observability`, `src/services`, `src/worker`
  - repo-local `__pycache__` roots outside `.venv`
  - ignored `agent/tmp_run_logs/`
- moved clearly historical root material into the archive home:
  - `old/` -> `archive/code/old/`
  - `notebooks/` -> `archive/work/notebooks/`
  - `test.ipynb` -> `archive/work/notebooks/test.ipynb`
- aligned archive/workflow references:
  - `archive/README.md`
  - `.github/workflows/deploy_yc_function_main.yml`
  - `.github/workflows/release_yc_function_prod.yml`
- verification:
  - `python scripts/check_no_legacy_entrypoint_imports.py`
  - `python scripts/render_grafana_dashboard.py --help`
  - `python scripts/provision_grafana_dashboard.py --help`
  - `python scripts/provision_grafana_datasource.py --help`
  - `python scripts/provision_datalens_dashboard.py --help`
  - `python -m unittest tests.architecture.test_guardrails_v0 tests.entrypoints.test_import_safety tests.entrypoints.test_planner_runtime_entry tests.api.test_frontend_api_routing tests.api.test_info_observability tests.platform.runtime.test_queue_dispatch -v`
- new blocker discovered during hygiene verification:
  - active runtime and tests still depend broadly on the root `core/` package
  - `src/core/` also exists as a second domain-looking root
  - this is no longer a cleanup-only smell; it is a real architecture decision about the canonical domain root
