# Dedup Plan (Current)

This document tracks active duplicate/parallel implementations and defines `keep/remove` targets for `CAM-DEDUP-LEGACY-REMOVAL-V1`.

## Runtime boundary
- Active runtime path: `main.py` + `index.py` + `src/entrypoints/*` + `src/services/pipeline_runtime.py`.
- `old/*` and notebooks are explicitly out of scope by owner decision.

## Duplicate map
| role | keep | remove/deprecate | usage evidence | risk |
|---|---|---|---|---|
| Sync service | `src/services/sync_service.py::YdbSyncService` | `src/services/sync/sync_service.py::SyncService` | runtime imports use `src/services/sync_service.py` (`src/services/pipeline_runtime.py`); legacy sync handler imports `src/services/sync/sync_service.py` only | medium (legacy handler tests rely on old module) |
| Readmodel builder | `src/services/readmodel_builder.py::FrontendReadmodelBuilderService` | `src/services/readmodels/builder.py::build_read_models` for runtime contour | runtime imports use `src/services/readmodel_builder.py`; `src/services/readmodels/builder.py` used by legacy handler tests | medium |
| Readmodel publisher | `src/adapters/ydb/readmodel_repo.py` + runtime builder upsert path | `src/services/readmodels/publisher.py` file-based artifact publisher in runtime contour | no active runtime imports to publisher; covered by legacy tests only | low |
| Sync/build handlers | entrypoints/jobs + `src/services/pipeline_runtime.py` | `src/handlers/sync.py`, `src/handlers/build_readmodels.py` in runtime contour | no imports from `main.py`/`index.py`; only handler tests use them | medium (sync handler removed 2026-03-04) |

## Proposed removal sequence
1. Add explicit `legacy-only` marking in docs for handler/readmodels old path.
2. Stop running legacy handler tests in default smoke (or move to dedicated legacy suite). (done for sync handler path via deletion)
3. Remove remaining legacy handler path and `src/services/sync/sync_service.py` after test suite split.
4. Remove `src/services/readmodels/*` runtime-irrelevant builder/publisher path after migration note is documented.

## Guardrails
- Remove only one duplicate branch per PR.
- Keep behavior-equivalent runtime smoke green (`tests.services.*` + `tests.api.*`).
- If any module is still imported by active runtime, do not remove it in the same PR where mapping is created.
