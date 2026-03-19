# Module Map (Current)

This document maps the modules that matter for the active runtime contour.

Governing policy:
- [architecture-values.md](architecture-values.md)
- [modular-monolith-v2.md](modular-monolith-v2.md)

## Active runtime entrypoints

| Path | Role | Responsibility | State | Notes |
|---|---|---|---|---|
| `index.py` | Entrypoint | Thin runtime shell for cloud events | OK | Lazy bootstrap and dispatch only. |
| `src/entrypoints/index_dispatcher.py` | Entrypoint | Classify event shape and delegate to the correct shell | OK | Canonical top-level router. |
| `src/entrypoints/http/*` | Entrypoint | HTTP parsing, access boundary, handlers, response translation | OK | Canonical browser/API boundary. |
| `src/entrypoints/queue/*` | Entrypoint | Queue-trigger transport shell | OK | Canonical worker intake boundary. |
| `src/entrypoints/triggers/*` | Entrypoint | Scheduled-trigger intake and queue fan-out | OK | Canonical trigger boundary. |
| `src/entrypoints/runtime/*` | Entrypoint | Explicit runtime-mode bridge for local/manual execution | OK | Includes the transitional adapter used by local/runtime shells. |

## Active domain and application areas

| Path | Role | Responsibility | State | Notes |
|---|---|---|---|---|
| `src/core/models/*` | Domain | Canonical domain DTOs | OK | Pure contracts only. |
| `src/core/normalize/*` | Domain | Normalization, parsing, inference rules | OK | Pure business logic. |
| `src/core/rules/*` | Domain | Domain rules and invariants | OK | Keep pure and tested. |
| `src/snapshot_engine/*` | Application | Snapshot build, query, cache, and storage access | OK | Canonical read-side engine. |
| `src/commands/*` | Application | Internal command contracts and queue serialization | OK | Canonical async command boundary. |
| `src/worker/*` | Application | Worker dispatcher, execution, status persistence | OK | Canonical async mutation runner. |
| `src/jobs/*` | Application | Concrete snapshot/render/reminder jobs | OK | Canonical mutation jobs. |
| `src/services/access/*` | Application | Access context masking and payload transforms | OK | Browser access policy lives at the boundary. |
| `src/notify/*` | Application | Reminder formatting and delivery orchestration | Frozen | Operational but not target for redesign in this wave. |
| `src/telegram/*` | Adapter/Application boundary | Telegram parsing, routing, webhook intake, sender | Frozen | Operational but not target for redesign in this wave. |
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
- `src/legacy/*`
- `old/v1/*`
- planner-era extraction plans and compatibility notes under `docs/archive/system_legacy/modules/*`
- legacy YDB/readmodel/schema material under `docs/archive/system_legacy/ydb_schema.md`

If a reader needs that history, current docs should point there instead of retelling it here.

## Immediate guidance

- Keep `index.py` thin.
- Treat `src/snapshot_engine/*` as the canonical read-side runtime.
- Keep browser auth and masking at the HTTP/access boundary.
- Keep refresh/render/reminder work in async jobs or explicit runtime modes.
- Treat archive modules and docs as reference-only, not as active architecture.
- Use `modular-monolith-v2.md` and companion ownership docs as the canonical target map for future extraction waves.
