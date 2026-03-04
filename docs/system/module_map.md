# Module map (Current)

This document is a **navigation map** of the codebase as it exists today. It is not a target architecture.

## Legend
- **Role**: Domain / Application / Adapter / Entrypoint / Support / Legacy
- **State**: OK (keep), Refactor (keep but move/reshape), Legacy (replace/retire), Experimental

## Top-level entrypoints

| Path | Role | Responsibility | Key imports / deps | State | Notes |
|---|---|---|---|---|---|
| `index.py` | Entrypoint (HTTP) | Cloud Functions / API Gateway orchestration: parse event, dispatch HTTP handlers, trigger planner runtime modes | mostly `src/entrypoints/http/*` modules + boundary wiring to planner/YDB deps | Refactor | Significantly thinned, but still contains runtime orchestration and dependency wiring that should move to dedicated handler/composition module. |
| `main.py` | Entrypoint (Jobs) | Orchestrates timer/test/morning/reminders-only/sync-only/db_migrate; hash gate; YDB sync; readmodel build | `GoogleSheetPlanner`, `OperationalTaskRepo`, `YdbSyncService`, `FrontendReadmodelBuilderService`, config/constants | Refactor | Acts as “god runner”. Should be split into job modules + service calls. |
| `local_run.py` | Support | Local wrapper to run modes (dev convenience) | uses `main.main()` | OK | Keep as developer tool, but should target new job entrypoints after refactor. |

## Source of tasks (Sheets)

| Path | Role | Responsibility | State | Notes |
|---|---|---|---|---|
| `core/` (folder) | Legacy (mixed) | Old architecture: planner/use_cases/repository/read_model/api_payload/render/notify | Legacy | Coexists with `src/*`. Biggest source of confusion and duplication. |
| `core/manager.py`, `core/planner.py`, `core/use_cases.py` | Legacy (application) | Orchestration around Sheets-based pipeline | Legacy | Used by `main.py` via `GoogleSheetPlanner`. |
| `core/repository.py` | Legacy (data access) | Task repository over Sheets | Legacy | Should be replaced by adapter + domain normalization. |

## Domain (new)

| Path | Role | Responsibility | State | Notes |
|---|---|---|---|---|
| `src/core/models/*` | Domain | Domain contracts / DTOs | OK | Keep as canonical domain types. |
| `src/core/normalize/*` | Domain | Normalization and date inference (incl. year inference for milestones) | OK | Business logic; should remain pure. |
| `src/core/rules/*` | Domain | Pure rules (priorities, etc.) | OK | Keep pure and tested. |

## Application services (new)

| Path | Role | Responsibility | State | Notes |
|---|---|---|---|---|
| `src/services/sync_service.py` | Application | YDB sync orchestration: hash gate (preflight+full), normalize payloads, versioning, write operational tables | OK / Refactor | Looks like primary sync path. Duplicates exist in `src/services/sync/*`. |
| `src/services/readmodel_builder.py` | Application | Bulk-load operational head + versioned milestones, build frontend v2 snapshot | OK | Should be the only builder used by API v2. |
| `src/services/source_policy.py` | Application | Decide which data source to use for render/notify per mode | Refactor | Policy is fine, but wiring should live in bootstrap, not in main.py. |
| `src/services/sync/` | Application support | Hash-basis/hash-gate primitives shared by runtime helpers | Refactor | Legacy `sync_service.py` duplicate removed; keep only stateless primitives. |
| `src/services/render/*` | Application | Rendering jobs (Sheets renderer) | Refactor | Ensure it reads from readmodel/operational bulk, not Sheets directly. |
| `src/services/notify/*` | Application | Reminder selection + formatting pipeline | Refactor | Ensure no N+1 YDB calls; prefer readmodel. |
| `src/services/readmodels/*` | Legacy | Legacy readmodel wrapper path | Removed | Removed from active tree in dedup wave; runtime uses `src/services/readmodel_builder.py`. |

## Handlers (new)

| Path | Role | Responsibility | State | Notes |
|---|---|---|---|---|
| `src/handlers/api.py` | Legacy | Placeholder API handler skeleton | Removed | Removed from active tree in dedup wave; runtime uses `src/entrypoints/http/*`. |
| `src/handlers/build_readmodels.py` | Legacy | Legacy build-readmodels handler | Removed | Removed from active tree in dedup wave. |
| `src/handlers/render_sheets.py` | Legacy | Placeholder render handler | Removed | Removed from active tree in dedup wave. |
| `src/handlers/notify_morning.py` | Legacy | Placeholder notify handler | Removed | Removed from active tree in dedup wave. |

## Adapters (integrations)

| Path | Role | Responsibility | State | Notes |
|---|---|---|---|---|
| `src/adapters/ydb/client.py` | Adapter | YDB client wrapper, retries/backoff stats | OK | Keep; ensure used everywhere for YDB access. |
| `src/adapters/ydb/schema.py` | Adapter | DDL (ensure tables) | OK | DDL must not run in hot path except explicit migrate mode. |
| `src/adapters/ydb/operational_repo.py` | Adapter | YDB repo for dtm_tasks, dtm_task_versions, dtm_task_milestones_v, dtm_sync_state | OK | Canonical operational store.
| `src/adapters/ydb/readmodel_repo.py` | Adapter | YDB repo for dtm_readmodel_frontend_v2 | OK | Canonical snapshot store.
| `src/adapters/store_ydb.py` | Adapter (legacy) | Legacy blob/payload store `dtm_operational_tasks` | Legacy | Should be off by default; keep only for rollback window.
| `src/adapters/*telegram*` | Adapter | Telegram send | OK | |
| `src/adapters/*sheets*` | Adapter | Sheets read/write, renderer | Refactor | Split “read snapshot” vs “heavy render formatting”. |
| `src/adapters/*llm*` | Adapter | LLM enhancements | Refactor | Needs config cleanup; env overload today. |

## Config / support

| Path | Role | Responsibility | State | Notes |
|---|---|---|---|---|
| `config/constants.py` | Support (config) | Loads env and defines many runtime switches | Refactor | Too much in env; later campaign should move non-secrets to config files. |
| `utils/*` | Support | Helpers | OK | Keep small; avoid business logic here. |
| `agent/*` | Support | One-off scripts, migrations, helpers | OK | Keep but separate from runtime code.
| `tests/*` | Support | Unit tests | OK | Expand coverage for new architecture boundaries.
| `old/`, `web_prototype/` | Experimental | Prototypes / legacy | Experimental | Should be clearly labeled and excluded from runtime imports.

## Known duplications / conflicts (to resolve)

1) **Two sync implementations**: `src/services/sync_service.py` vs `src/services/sync/*` (legacy handler removed from active tree).
2) **Two cores**: top-level `core/` (legacy mixed) vs `src/core/` (domain).
3) **Legacy handler stubs removed**: runtime now relies on `src/entrypoints/http/*` and `src/entrypoints/jobs/*` instead of `src/handlers/*`.

## Immediate recommendations

- Treat `src/*` as the target structure; treat top-level `core/` as legacy.
- Keep `index.py` thin: event parsing + routing in `src/entrypoints/http/*`.
- Keep `main.py` thin: mode selection + orchestration delegated to `src/entrypoints/jobs/*`.
- Consolidate sync path: pick one implementation and archive/remove the other.
