# CAM-2026-03-12-RUNTIME-DEPLANNERIZE-AND-BOOTSTRAP-HARDENING-V1

## Goal

Zero runtime side effects on module import for main entrypoints, with planner-centric top runtime reduced to a transitional adapter and no production bootstrap at import time.

## Scope

In scope:
- `index.py`
- `src/app/bootstrap.py`
- `src/entrypoints/index_dispatcher.py`
- `src/entrypoints/runtime/planner_runtime_entry.py`
- direct callers of planner runtime helpers

Out of scope:
- auth/masking implementation
- Telegram/reminder redesign
- large query-engine rewrite

## Concrete tasks

1. Verify current import-time bootstrap side effects and active planner-centric call paths.
2. Introduce explicit runtime action seams instead of global runtime context.
3. Reduce `planner_runtime_entry.py` to transitional adapter behavior.
4. Make active runtime imports safe under stripped env.
5. Record remaining transitional legacy couplings.

## Acceptance criteria

- `index.py` does not construct `AppContext` on module import
- `src/entrypoints/runtime/planner_runtime_entry.py` does not construct `AppContext` on module import
- `build_app_context()` is called only from explicit runtime entry or factory boundaries
- import of `index.py` and `planner_runtime_entry.py` is safe in tests without production env
- planner runtime is transitional, not conceptual center
- import-safe smoke exists for active runtime modules
- evidence captures before/after import behavior
