# Module map (Current)

This document is a navigation map of the codebase as it exists now.

## Top-level entrypoints

| Path | Role | Responsibility | State | Notes |
|---|---|---|---|---|
| `index.py` | Entrypoint (HTTP) | Parse event, dispatch HTTP handlers, optionally trigger planner runtime modes | Refactor | Thin shell; uses `src/entrypoints/http/*` and shared runtime entry. |
| `src/entrypoints/runtime/planner_runtime_entry.py` | Entrypoint (Runtime) | Canonical planner runtime orchestration for local/job and HTTP-triggered modes | OK | Single standard runtime entry used by `index.py` and `src/entrypoints/runtime/local_runtime.py`. |
| `local_run.py` | Support | Local wrapper for runtime modes | OK | Dev convenience tool; calls `src/entrypoints/runtime/local_runtime.py`. |

## Entrypoint boundaries

| Path | Role | Responsibility | State | Notes |
|---|---|---|---|---|
| `src/entrypoints/http/*` | Entrypoint (HTTP modules) | HTTP parsing/routing/handlers/runtime execution helpers | OK | Canonical HTTP boundary. |
| `src/entrypoints/jobs/*` | Entrypoint (Jobs modules) | Runtime job steps used by planner runtime entry | OK | Active standard-runtime job modules only. |

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
| `src/legacy/*` | Legacy | Archived planner/bootstrap/render/reference contour, including legacy core/bootstrap/use-case shims | Legacy | Reference-only; must not be imported by standard runtime. |
| `core/*` | Domain/compat mix | Domain contracts still used by live features; legacy compatibility shims removed from active root | Refactor | `core/bootstrap.py` and `core/manager.py` are archived under `src/legacy/core/`. |
| `old/v1/*` | Legacy archive | Historical v1 artifacts | Legacy | Preserved as archaeology; not active runtime path. |

## Immediate guidance

- Keep `index.py` thin; local tooling should use `src/entrypoints/runtime/local_runtime.py`.
- Keep planner runtime orchestration in `src/entrypoints/runtime/planner_runtime_entry.py`.
- Keep API/runtime route logic in `src/entrypoints/http/*`.
- Keep legacy bindings explicit under `src/legacy/*` only; do not recreate compat shims in active `core/`.
