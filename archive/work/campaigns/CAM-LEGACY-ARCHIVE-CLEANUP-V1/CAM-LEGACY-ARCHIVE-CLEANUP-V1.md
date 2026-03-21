# CAM-LEGACY-ARCHIVE-CLEANUP-V1

## Goal
- move dead-end planner/bootstrap/render/readmodel-probe modules out of the active tree
- remove `main.py` from active local/runtime usage
- keep legacy code as reference-only under `src/legacy/`

## Scope
- add `src/entrypoints/runtime/local_runtime.py`
- rewire `local_run.py`
- archive `main.py`
- archive old planner/bootstrap/render stack and readmodel-probe helpers
- archive compat `core/bootstrap.py`, `core/manager.py`, and old planner use-case shim
- update guards, docs, and tracking

## DoD
- active runtime/tooling no longer imports `main.py`
- active runtime/tooling no longer imports old planner/bootstrap/render/readmodel-probe modules from active paths
- legacy reference code lives under `src/legacy/`
- guard script blocks reintroduction
- active root no longer contains legacy compat bootstrap/manager/use-case modules
