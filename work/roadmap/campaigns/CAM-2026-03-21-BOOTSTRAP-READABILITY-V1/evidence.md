# CAM-2026-03-21-BOOTSTRAP-READABILITY-V1 Evidence

## Trust Gate

- source: `docs/architecture/module-first-recovery/repo-beauty-audit-2026-03-21.md`
  - last_verified_at: `2026-03-21`
  - verified_by: `Codex`
  - evidence: bootstrap readability is the next remaining high-signal structural beauty smell after top-path, naming, and docs voice cleanup
  - trust_level: `high`
  - notes: the issue is no longer about code ownership, only about readability and finish quality

- source: bootstrap contour and dependent seams
  - last_verified_at: `2026-03-21`
  - verified_by: `Codex`
  - evidence:
    - `src/platform/bootstrap.py`
    - `src/platform/app_context.py`
    - `tests/api/test_frontend_api_routing.py`
    - `tests/api/test_command_queue_foundation.py`
    - `src/entrypoints/runtime/planner_runtime_entry.py`
  - trust_level: `high`
  - notes: enough code evidence exists to finish the readability pass without changing runtime behavior

## Completed Tasks

- [x] `CAM-2026-03-21-BOOTSTRAP-READABILITY-V1-P01-T001` remove mutable bootstrap seams from `index.py` and the nearest active tests
- [x] `CAM-2026-03-21-BOOTSTRAP-READABILITY-V1-P02-T001` replace `APP_DEPS` / `APP_TRIGGERS` with explicit runtime getters
- [x] `CAM-2026-03-21-BOOTSTRAP-READABILITY-V1-P03-T001` verify the top path, command queue, info/API, and import-safety contours after the cleanup

## Verification

- `python -m unittest tests.entrypoint.test_handler tests.api.test_frontend_api_routing tests.api.test_info_observability tests.api.test_command_queue_foundation tests.architecture.test_guardrails_v0 tests.entrypoints.test_import_safety tests.entrypoints.test_planner_runtime_entry -v`
- `rg -n "APP_DEPS|APP_TRIGGERS|_get_app_context|LazyMapping|get_deps\\(|get_triggers\\(" src tests docs work index.py`

## Verdict

- before: bootstrap readability was held back by mutable top-level seams and stale top-path mutation points that made the runtime contour look heavier than it really was
- after: the active top path now uses explicit platform getters, `index.py` no longer exports bootstrap mutation seams, and `src/platform/bootstrap.py` reads as neutral lazy runtime glue
- next worst thing: historical/runtime references were still slightly too visible from active runtime docs
