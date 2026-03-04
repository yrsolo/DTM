# Core Shim Deprecation Checklist

## Scope
Compatibility shims in:
- `core/repository.py`
- `core/people.py`
- `core/planner.py`
- `core/manager.py`

## Current usage audit (2026-03-04)

### Runtime paths (non-legacy)
- `src/app/planner_bootstrap.py` imports `TaskTimingProcessor` from `core.manager`.

### Tests/auxiliary
- none (tests and `agent/*_smoke.py` switched to `src/services/*` imports).

### Legacy/archive
- `old/*` still imports `core.repository`, `core.people`, `core.manager`, `core.planner`.
- `test.ipynb` imports `GoogleSheetPlanner` from `core.planner`.

## Deprecation steps
1. Switch `src/app/planner_bootstrap.py` to a non-shim source for `TaskTimingProcessor` (either dedicated core policy module or new service-domain module).
2. Policy decision for `old/*` and `test.ipynb` (owner decision, 2026-03-04):
   - keep legacy contour untouched,
   - keep compatibility re-exports for legacy imports.
3. Keep shim modules as thin long-term compatibility layer with explicit scope:
   - active runtime/test paths should not use shim imports,
   - legacy contour may continue using them.

## Exit criteria
- No active runtime/test/agent imports from shim modules.
- Legacy-only shim usage limited to `old/*` and notebooks by owner policy.
