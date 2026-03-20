# Module Map (Current)

This document maps the modules that matter for the active runtime contour.

Governing policy:
- [architecture-values.md](architecture-values.md)
- [../module-first-recovery/README.md](../module-first-recovery/README.md)

## Active runtime entrypoints

| Path | Role | Responsibility | State | Notes |
|---|---|---|---|---|
| `index.py` | Entrypoint | Thin runtime shell for cloud events | OK | Lazy bootstrap and dispatch only. |
| `src/entrypoint/*` | Entrypoint | Thin entrypoint layer for parsed request routing | OK | Canonical intake surface. |
| `src/entrypoints/http/*` | Entrypoint | HTTP parsing, transport routing, and response-shell logic over context-owned handlers | OK | Browser/API transport boundary; access-api-owned handlers now live under `src/contexts/access_api/internal/*`. |
| `src/entrypoints/queue/*` | Entrypoint | Queue-trigger transport shell | OK | Canonical worker intake boundary. |
| `src/entrypoints/triggers/*` | Entrypoint | Scheduled-trigger intake and queue fan-out | OK | Canonical trigger boundary. |
| `src/entrypoints/runtime/*` | Entrypoint | Explicit runtime-mode bridge for local/manual execution | OK | Canonical local/runtime shell boundary. |

## Active domain and application areas

| Path | Role | Responsibility | State | Notes |
|---|---|---|---|---|
| `src/platform/*` | Platform | Runtime wiring, queue/runtime orchestration, bootstrap delegation | OK | Platform owns transport/runtime only. |
| `src/contexts/attachments/*` | Context | Attachment lifecycle and attachment access policy | OK | First fully extracted context. |
| `src/contexts/reminders/*` | Context | Reminder execution ownership and public facade | OK | Trigger intake stays platform-owned. |
| `src/contexts/snapshot/*` | Context | Snapshot public API, contracts, internal engine, and read-side ownership | OK | Canonical cross-context snapshot surface and internal engine home. |
| `src/contexts/rendering/*` | Context | Rendering ownership and snapshot-boundary enforcement | OK | Depends on `snapshot.public` or contracts only. |
| `src/contexts/telegram_interaction/*` | Context | Telegram interaction ownership and command routing facade | OK | Owns `group_query_reply`. |
| `src/contexts/access_api/*` | Context | Browser-facing read surface ownership and access policy facade | OK | Owns frontend root, frontend v2, info, people snapshot, and attachment read handlers. |
| `src/core/models/*` | Domain | Canonical domain DTOs | OK | Pure contracts only. |
| `src/core/normalize/*` | Domain | Normalization, parsing, inference rules | OK | Pure business logic. |
| `src/core/rules/*` | Domain | Domain rules and invariants | OK | Keep pure and tested. |
| `src/commands/*` | Application | Internal command contracts and queue serialization | OK | Canonical async command boundary. |
| `src/worker/*` | Application | Worker dispatcher, execution, status persistence | OK | Canonical async mutation runner. |
| `src/services/access/*` | Application | Access context masking and payload transforms | OK | Browser access policy lives at the boundary. |
| `src/observability/*` | Support | Metrics, logging, timing, trace helpers | OK | Shared observability layer. |
| `src/config/*` | Support | Typed config schema and loader | OK | Canonical config source of truth. |
| `src/app/bootstrap.py` | Support | Composition root and dependency assembly | OK | Bootstrap only; no business logic. |

## Active adapters

| Path | Role | Responsibility | State | Notes |
|---|---|---|---|---|
| `src/adapters/*sheets*` | Adapter | Google Sheets fetch/update integrations | OK | Edge adapter for source data and render writes. |
| `src/adapters/telegram.py` | Adapter | Telegram delivery integration | OK | Used by notify and group-query flows. |
| `src/adapters/llm_*` | Adapter | Optional LLM enhancement providers | OK | Optional edge integrations only. |

## Historical or archive-only areas

These are not part of the canonical runtime story:
- `src/archive/legacy_runtime/*`
- removed compatibility-only roots formerly used during recovery:
  - `src/jobs/*`
  - `src/render/*`
  - `src/notify/*`
  - `src/telegram/*`
  - `src/services/attachments/*`
  - `src/snapshot_engine/*`
- `archive/legacy_test_refs/*`
- `old/v1/*`
- planner-era extraction plans and compatibility notes under `docs/archive/system_legacy/modules/*`
- legacy YDB/readmodel/schema material under `docs/archive/system_legacy/ydb_schema.md`

If a reader needs that history, current docs should point there instead of retelling it here.

## Immediate guidance

- Keep `index.py` thin.
- Treat `src/contexts/*` and `src/platform/*` as the canonical target ownership map for active refactor work.
- Treat `src/contexts/snapshot/internal/engine/*` as the canonical internal read-side runtime.
- Keep browser auth, read shaping, and masking inside `access_api`; keep `src/entrypoints/http/*` transport-only.
- Keep refresh/render/reminder work in async jobs or explicit runtime modes.
- Treat archive modules and docs as reference-only, not as active architecture.
- Use the module-first recovery canon and companion ownership docs as the canonical target map for future extraction waves.
