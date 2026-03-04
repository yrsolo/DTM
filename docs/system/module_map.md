# Module map (Current)

This document is a navigation map of the codebase as it exists now.

## Top-level entrypoints

| Path | Role | Responsibility | State | Notes |
|---|---|---|---|---|
| `index.py` | Entrypoint (HTTP) | Parse event, dispatch HTTP handlers, optionally trigger planner runtime modes | Refactor | Thin shell; uses `src/entrypoints/http/*` and shared runtime entry. |
| `main.py` | Entrypoint (Jobs) | Thin wrapper over shared runtime entry | OK | Delegates to `run_planner_runtime(...)` only. |
| `src/entrypoints/runtime/planner_runtime_entry.py` | Entrypoint (Runtime) | Canonical planner runtime orchestration for job and HTTP-triggered modes | OK | Single runtime entry used by both `main.py` and `index.py`. |
| `local_run.py` | Support | Local wrapper for runtime modes | OK | Dev convenience tool. |

## Entrypoint boundaries

| Path | Role | Responsibility | State | Notes |
|---|---|---|---|---|
| `src/entrypoints/http/*` | Entrypoint (HTTP modules) | HTTP parsing/routing/handlers/runtime execution helpers | OK | Canonical HTTP boundary. |
| `src/entrypoints/jobs/*` | Entrypoint (Jobs modules) | Runtime job steps used by planner runtime entry | OK | Active job orchestration modules. |
| `src/legacy/http_core_bindings.py` | Legacy bridge | Isolates legacy core composition bindings for HTTP contour | Legacy (contained) | Explicitly isolated legacy namespace. |

## Domain (new)

| Path | Role | Responsibility | State | Notes |
|---|---|---|---|---|
| `src/core/models/*` | Domain | Domain contracts and DTOs | OK | Canonical domain types. |
| `src/core/normalize/*` | Domain | Normalization/date inference rules | OK | Pure business logic. |
| `src/core/rules/*` | Domain | Pure domain rules | OK | Keep pure and tested. |

## Application services

| Path | Role | Responsibility | State | Notes |
|---|---|---|---|---|
| `src/services/sync_service.py` | Application | Canonical sync orchestration and preflight/full decision path | OK | Single active sync service in runtime. |
| `src/services/readmodel_builder.py` | Application | Build frontend v2 readmodel snapshot | OK | Canonical snapshot builder. |
| `src/services/pipeline_runtime.py` | Application | YDB sync + readmodel pipeline orchestration | OK | Preflight can skip full snapshot fetch. |
| `src/services/sync/*` | Support | Sync helper primitives | Refactor | Keep only stateless primitives; no duplicate sync runner. |

## Adapters

| Path | Role | Responsibility | State | Notes |
|---|---|---|---|---|
| `src/adapters/ydb/*` | Adapter | YDB clients/repos/schema and readmodel/operational storage | OK | Canonical persistence boundary. |
| `src/adapters/store_ydb.py` | Adapter (legacy) | Legacy blob store write path | Legacy | Kept for compatibility windows. |
| `src/adapters/*sheets*` | Adapter | Google Sheets access and related integrations | Refactor | Runtime uses bulk snapshot reads where required. |
| `src/adapters/telegram.py` | Adapter | Telegram notifier integration | OK | Used by entrypoint runtime and group query flows. |

## Legacy and archive

| Path | Role | Responsibility | State | Notes |
|---|---|---|---|---|
| `core/*` | Legacy | Old architecture compatibility contour | Legacy | Kept for controlled legacy compatibility only. |
| `old/v1/*` | Legacy archive | Historical v1 artifacts | Legacy | Preserved as archaeology; not active runtime path. |

## Immediate guidance

- Keep `index.py` and `main.py` thin wrappers.
- Keep planner runtime orchestration in `src/entrypoints/runtime/planner_runtime_entry.py`.
- Keep API/runtime route logic in `src/entrypoints/http/*`.
- Keep legacy bindings explicit under `src/legacy/*` only.
