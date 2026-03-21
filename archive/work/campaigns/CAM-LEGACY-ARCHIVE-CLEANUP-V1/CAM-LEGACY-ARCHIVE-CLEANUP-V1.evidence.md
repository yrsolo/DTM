# CAM-LEGACY-ARCHIVE-CLEANUP-V1 Evidence

- source: code scan of `local_run.py`, `core/bootstrap.py`, `core/manager.py`, `src/legacy/*`, and active entrypoint/runtime imports
- last_verified_at: 2026-03-09
- verified_by: Codex
- trust_level: high

## Verified facts
- `main.py` was only used by `local_run.py`
- standard runtime feature paths did not require:
  - `src/app/planner_bootstrap.py`
  - `src/services/planner_runtime.py`
  - `src/services/calendar_runtime.py`
  - `src/services/render/task_table_runtime.py`
  - `src/entrypoints/jobs/readmodel_probe_job.py`
  - `src/entrypoints/jobs/readmodel_freshness.py`
- offline tooling and compatibility shims still referenced parts of the old planner stack

## Applied cut
- added `src/entrypoints/runtime/local_runtime.py`
- switched `local_run.py` away from `main.py`
- archived `main.py` to `src/legacy/main.py`
- moved planner/bootstrap/render/readmodel-probe modules under `src/legacy/`
- moved compat `core/bootstrap.py`, `core/manager.py`, and `src/services/usecases/planner_runtime.py` under `src/legacy/`
- moved legacy/reference tests out of active `tests/services` and `tests/core` buckets
- moved stale active system docs/checklists/plans from `docs/system/` to `archive/docs/system_legacy/`
- rewrote active `docs/system/architecture.md`, `runtime_modes.md`, `config.md`, and `README.md` to reflect the current snapshot/queue/runtime contour
- updated compatibility/tooling imports to explicit `src.legacy.*`
- extended `scripts/check_no_legacy_entrypoint_imports.py`

## Validation
- active import scan after move shows no active imports from the archived planner stack
- local runtime remains available through `local_run.py`
- active root no longer contains `main.py`, `core/bootstrap.py`, `core/manager.py`, or `src/services/usecases/planner_runtime.py`

