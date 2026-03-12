# CAM-ENTRYPOINT-LEGACY-CUT-FINAL-V1

## Goal
Make `index.py` a thin shell, remove dead-end legacy runtime branches from standard entrypoint flow, and archive remaining reference-only code outside active runtime imports.

## Scope
- thin `index.py` through dispatcher + transport shells
- remove `FrontendReadmodelRepo` leakage from HTTP entrypoint path
- cut legacy planner/store/readmodel-probe branch from standard runtime
- archive dead-end entrypoint jobs under `src/legacy/`
- add grep gate preventing legacy imports from active entrypoints/runtime

## Non-goals
- no Snapshot Engine rewrite
- no API contract changes
- no queue topology changes
- no cleanup of broader `core/*` debt unless it blocks entrypoint cut

## Phases

### P01 — Trust Gate
- verify `index.py`, `router.py`, `planner_runtime_entry.py`, `main.py`
- map live product features to current runtime paths
- record dead-end legacy branches

### P02 — Thin Index
- add event classifier
- add index dispatcher
- add HTTP/queue/trigger/runtime shells
- reduce `index.py` to app bootstrap + dispatcher call
- remove `FrontendReadmodelRepo` leak from router/frontend handler path

### P03 — Standard Runtime Cut
- remove `legacy_planner_*` support from standard runtime
- remove legacy store write / readmodel probe / planner use-case branch
- make unsupported modes explicit

### P04 — Archive + Guards
- move dead-end entrypoint jobs to `src/legacy/entrypoints/jobs/`
- add grep gate blocking legacy imports in active runtime files

### P05 — Verification + Docs
- run routing/runtime regression tests
- update docs and tracking

## DoD
- `index.py` imports only `build_app_context` and `IndexDispatcher`
- `HttpRouter` no longer accepts `frontend_readmodel_repo_cls`
- `FrontendV2Handler` no longer accepts unused repo parameter
- `planner_runtime_entry.py` contains no `use_legacy_planner` branch
- standard runtime supports only live product features
- active entrypoints/runtime do not import legacy planner/store branches
- grep gate enforces no relapse
