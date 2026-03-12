# Module map (Current)

This document is a navigation map of the codebase as it exists now.

Governing policy:
- [architecture_values.md](/n:/PROJECTS/python/SCRIPT/DTM/docs/system/architecture_values.md)

## Top-level entrypoints

| Path | Role | Responsibility | State | Notes |
|---|---|---|---|---|
| `index.py` | Entrypoint (HTTP) | Parse event, dispatch HTTP handlers, optionally trigger runtime actions | Refactor | Thin shell; current code still has import-time bootstrap and must move to explicit runtime boundaries. |
| `src/entrypoints/runtime/planner_runtime_entry.py` | Entrypoint (Runtime) | Transitional runtime adapter for local/job and HTTP-triggered modes | Refactor | Still active, but should stop being the conceptual runtime center in the 2026-03-12 wave. |
| `local_run.py` | Support | Local wrapper for runtime modes | OK | Dev convenience tool; calls `src/entrypoints/runtime/local_runtime.py`. |

## Entrypoint boundaries

| Path | Role | Responsibility | State | Notes |
|---|---|---|---|---|
| `src/entrypoints/http/*` | Entrypoint (HTTP modules) | HTTP parsing/routing/handlers/runtime execution helpers | OK | Canonical HTTP boundary. |
| `src/entrypoints/jobs/*` | Entrypoint (Jobs modules) | Runtime job steps used by planner runtime entry | OK | Active standard-runtime job modules only. |
| `src/entrypoints/http/access*` | Entrypoint (planned access boundary) | Browser access context resolution and trusted ingress handling | Planned | Target placement for full vs masked browser access logic. |

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
| `src/services/access/*` | Application (planned) | Masking policy, deterministic mapping, and payload transform seams | Planned | Preferred placement for browser masked/full access implementation. |
| `src/services/sync/*` | Support | Sync helper primitives | Refactor | Keep only stateless primitives; no duplicate sync runner. |
| `src/observability/*` | Support | Metrics, timing, and structured logging abstractions | OK | Shared instrumentation layer for active runtime. |

## Messaging and worker

| Path | Role | Responsibility | State | Notes |
|---|---|---|---|---|
| `src/commands/*` | Application | Internal queue command DTOs, serializer, queue adapters | OK | Canonical async command boundary. |
| `src/worker/*` | Application | Worker execution, dispatcher, status store | OK | Canonical queue execution boundary. |
| `src/telegram/*` | Adapter/Application boundary | Typed Telegram parsing, command routing, webhook intake, sender | Frozen | Keep operational, but not the target model for new architecture during this wave. |

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
- Treat `src/entrypoints/runtime/planner_runtime_entry.py` as transitional and reduce it over time.
- Keep API/runtime route logic in `src/entrypoints/http/*`.
- Keep browser auth and masking outside query-engine internals.
- Treat `src/telegram/*` and `src/notify/*` as frozen subsystems for this wave.
- Keep legacy bindings explicit under `src/legacy/*` only; do not recreate compat shims in active `core/`.
