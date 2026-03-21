# Context Ownership Map

This document maps ownership for the active module-first runtime.

Governing source:
- [../module-first-recovery/README.md](../module-first-recovery/README.md)

## First-class contexts

| Context | Owns | Current active areas |
|---|---|---|
| `snapshot` | ingestion, normalization, prepared state, query-facing state contracts | `src/core/*`, `src/contexts/snapshot/adapters/sources/*`, `src/contexts/snapshot/internal/engine/*`, `src/contexts/snapshot/application/update_job.py` |
| `rendering` | timeline/designers render plans and sheet writeback | `src/contexts/rendering/internal/*`, context-owned render jobs, sheets render adapters |
| `reminders` | reminder selection, payload building, styling, delivery orchestration | `src/contexts/reminders/internal/*`, context-owned reminder jobs |
| `telegram_interaction` | Telegram webhook intake, update parsing, update-to-command mapping, group/user interaction flows | `src/contexts/telegram_interaction/internal/*`, context-owned group-query job, Telegram-related HTTP intake |
| `attachments` | request upload, finalize, metadata lifecycle, preview lifecycle, delete lifecycle, read/view/download policy | `src/contexts/attachments/internal/*`, attachment HTTP handlers, attachment jobs, attachment paths in snapshot internal engine |
| `access_api` | frontend-facing HTTP surface, masked/open access policy, browser-safe DTO assembly | `src/entrypoints/http/frontend_*`, access masking, browser-facing query adapters |

## Platform-owned surfaces

These surfaces are not first-class business contexts. They remain owned by platform/runtime until explicitly split further.

| Surface | Owner | Current active areas |
|---|---|---|
| healthcheck | `platform.runtime` | event classification + top-level dispatch |
| info/admin ops | `platform.runtime` with explicit route ownership docs | `/info`, admin ops, diagnostics handlers |
| queue status / job status surfaces | `platform.runtime` | worker status store, job status endpoints |
| observability / runtime diagnostics | `platform.runtime` | `src/platform/observability/*`, diagnostics/reporting paths |

## Boundary notes

- `entrypoint` owns only transport intake and delegation.
- `platform` owns runtime classification, queue intake/dispatch, triggers, config/bootstrap, and low-level infrastructure assembly.
- contexts own business use-cases and must expose public facades instead of leaking internals.

## Immediate guidance

- treat the current folder layout as the active ownership map
- preserve behavior first, then refine local ownership within modules
- do not let transport folders define the conceptual architecture
