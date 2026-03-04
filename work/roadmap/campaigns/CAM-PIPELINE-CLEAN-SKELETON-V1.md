# CAM-PIPELINE-CLEAN-SKELETON-V1

## Goal
Make the runtime pipeline explicit and thin at entrypoint level:
- `main.py` should orchestrate, not host helper logic;
- pipeline decisions should live in focused `src/services/*` and `src/entrypoints/jobs/*` modules;
- behavior stays unchanged.

## Scope
- Extract non-domain helper blocks from `main.py` into `src/entrypoints/jobs/*`.
- Keep sync/readmodel execution path intact.
- Track each extraction as atomic, reversible step with smoke checks.

## Non-goals
- No behavior rewrites of sync/readmodel business rules.
- No migration of `old/*` and notebooks.

## Phases
### P01 - Inventory and first extractions
- `PIPE-P01-T001`: capture current pipeline helper hotspots and extraction order.
- `PIPE-P01-T002`: extract readmodel freshness helper from `main.py` into `src/entrypoints/jobs/readmodel_freshness.py`.

### P02 - Continue entrypoint thinning
- `PIPE-P02-T001`: extract hash-gate block from `main.py` into dedicated jobs/service helper. (done)
- `PIPE-P02-T002`: extract legacy store-write logging block into dedicated jobs helper. (done)
- `PIPE-P02-T003`: extract task payload conversion helpers from `main.py` into dedicated jobs helper module. (done)

## DoD
- `main.py` contains only mode routing and high-level orchestration calls.
- Helper logic lives in dedicated modules and is covered by smoke checks.
