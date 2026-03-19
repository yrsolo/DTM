# Context Ownership Map

This document maps target ownership for the modular-monolith refactor wave.

Governing source:
- [modular-monolith-v2.md](modular-monolith-v2.md)

## First-class contexts

| Context | Owns | Current active areas to verify/migrate from |
|---|---|---|
| `snapshot` | ingestion, normalization, prepared state, query-facing state contracts | `src/core/*`, `src/services/sources/*`, `src/snapshot_engine/*`, `src/jobs/update_snapshot_job.py` |
| `rendering` | timeline/designers render plans and sheet writeback | `src/render/*`, `src/jobs/render_*`, sheets render adapters |
| `reminders` | reminder selection, payload building, styling, delivery orchestration | `src/notify/*`, `src/jobs/send_reminders_job.py` |
| `telegram_interaction` | Telegram webhook intake, update parsing, update-to-command mapping, group/user interaction flows | `src/telegram/*`, `src/jobs/group_query_reply_job.py`, Telegram-related HTTP intake |
| `attachments` | request upload, finalize, metadata lifecycle, preview lifecycle, delete lifecycle, read/view/download policy | `src/services/attachments/*`, attachment HTTP handlers, attachment jobs, attachment paths in snapshot engine |
| `access_api` | frontend-facing HTTP surface, masked/open access policy, browser-safe DTO assembly | `src/entrypoints/http/frontend_*`, access masking, browser-facing query adapters |

## Platform-owned surfaces

These surfaces are not first-class business contexts. They remain owned by platform/runtime until explicitly split further.

| Surface | Owner | Current active areas |
|---|---|---|
| healthcheck | `platform.runtime` | event classification + top-level dispatch |
| info/admin ops | `platform.runtime` with explicit route ownership docs | `/info`, admin ops, diagnostics handlers |
| queue status / job status surfaces | `platform.runtime` | worker status store, job status endpoints |
| observability / runtime diagnostics | `platform.runtime` | `src/observability/*`, diagnostics/reporting paths |

## Boundary notes

- `entrypoint` owns only transport intake and delegation.
- `platform` owns runtime classification, queue intake/dispatch, triggers, config/bootstrap, and low-level infrastructure assembly.
- contexts own business use-cases and must expose public facades instead of leaking internals.

## Immediate migration guidance

- treat current folder layout as source material, not as the target map
- preserve behavior first, then move ownership behind context facades
- do not let transport folders define the conceptual architecture after this wave starts

