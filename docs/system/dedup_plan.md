# Dedup Plan (Current)

This document tracks active duplicate/parallel implementations and defines `keep/remove` targets for `CAM-DEDUP-LEGACY-REMOVAL-V1`.

## Runtime boundary
- Active runtime path: `main.py` + `index.py` + `src/entrypoints/*` + `src/services/pipeline_runtime.py`.
- `old/*` and notebooks are explicitly out of scope by owner decision.

## Duplicate map
| role | keep | remove/deprecate | usage evidence | risk |
|---|---|---|---|---|
| Sync service | `src/services/sync_service.py::YdbSyncService` | `src/services/sync/sync_service.py::SyncService` | runtime imports use `src/services/sync_service.py` (`src/services/pipeline_runtime.py`); no active imports for `src/services/sync/sync_service.py` | low (removed 2026-03-04) |
| Readmodel builder | `src/services/readmodel_builder.py::FrontendReadmodelBuilderService` | `src/services/readmodels/builder.py::build_read_models` for runtime contour | runtime imports use `src/services/readmodel_builder.py`; no active imports to legacy builder | low (removed 2026-03-04) |
| Readmodel publisher | `src/adapters/ydb/readmodel_repo.py` + runtime builder upsert path | `src/services/readmodels/publisher.py` file-based artifact publisher in runtime contour | no active runtime imports to publisher | low (removed 2026-03-04) |
| Sync/build handlers | entrypoints/jobs + `src/services/pipeline_runtime.py` | `src/handlers/sync.py`, `src/handlers/build_readmodels.py` in runtime contour | no imports from `main.py`/`index.py`; only handler tests used them | low (removed 2026-03-04) |
| API handler skeleton | `src/entrypoints/http/*` dispatch chain | `src/handlers/api.py` placeholder | no runtime imports; only static leftover | low (removed 2026-03-04) |
| Render/notify handler skeletons | `src/entrypoints/jobs/*` + service use-cases | `src/handlers/render_sheets.py`, `src/handlers/notify_morning.py` placeholders | no runtime imports; static leftovers only | low (removed 2026-03-04) |
| Handlers package placeholder | `src/entrypoints/http/*`, `src/entrypoints/jobs/*` | `src/handlers/__init__.py` marker-only package | no runtime imports of `src.handlers` namespace | low (removed 2026-03-04) |
| Frontend v1 payload serializer | `core/api_payload_v2.py` | `core/api_payload.py` (legacy v1 payload builder) | no runtime/test imports in active contour | low (removed 2026-03-04) |
| Core compatibility shims | `src/*` direct modules | `old/v1/{people,planner,repository,use_cases}.py` | no direct imports in active code contour; moved to legacy archaeology archive | low (moved 2026-03-04) |

## Proposed removal sequence
1. Add explicit `legacy-only` marking in docs for handler/readmodels old path.
2. Stop running legacy handler tests in default smoke (or move to dedicated legacy suite). (done for sync handler path via deletion)
3. Remove remaining legacy handler path and `src/services/sync/sync_service.py` after test suite split. (done)
4. Remove `src/services/readmodels/*` runtime-irrelevant builder/publisher path after migration note is documented. (done)
5. Compatibility shims moved from `core/*` to `old/v1/*` as legacy archaeology; keep read-only.

## Guardrails
- Remove only one duplicate branch per PR.
- Keep behavior-equivalent runtime smoke green (`tests.services.*` + `tests.api.*`).
- If any module is still imported by active runtime, do not remove it in the same PR where mapping is created.
