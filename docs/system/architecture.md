# Architecture (Current)

## Purpose
DTM is a Cloud Functions runtime that:
- reads task data from Google Sheets,
- builds snapshot artifacts in Object Storage,
- serves API/query responses from prepared snapshots,
- renders operational Sheets views,
- sends Telegram notifications,
- executes heavy mutations asynchronously through Message Queue workers.

Governing architecture policy:
- [architecture_values.md](/n:/PROJECTS/python/SCRIPT/DTM/docs/system/architecture_values.md)

## Canonical production contour
1. Sheets snapshot (`values + colors`)
2. Normalize into canonical task model
3. Write Raw snapshot to S3/Object Storage
4. Merge Extra metadata and build Prep snapshot
5. Consumers read Prep snapshot

Consumers:
- `/api/v2/frontend`
- `/info`
- render jobs (`Задачи`, `Дизайнеры`)
- reminder jobs
- group query reply jobs

## Runtime topology
- `index.py` is a thin top-level shell.
- `src/entrypoints/index_dispatcher.py` classifies event shape.
- Transport shells handle:
  - HTTP
  - queue worker events
  - scheduled triggers
  - runtime execution bridge

Current architectural direction for the 2026-03-12 wave:
- remove import-time production bootstrap from active runtime modules,
- reduce planner runtime to a transitional adapter rather than the conceptual center,
- keep browser auth and masking at the access boundary,
- validate browser-facing trusted ingress with an internal proxy secret before honoring `x-dtm-*` auth headers,
- keep read endpoints cache-first and side-effect free by default.
- keep `/info` summary-first by default and expose heavy diagnostics only through explicit detail mode.
- treat Telegram/reminder/group-query as frozen unless break/fix work is required.

## Async mutation contour
Heavy and mutating actions are queue-backed:
- snapshot update
- render timeline sheet
- render designers sheet
- send reminders
- attach task file
- telegram group-query reply

Flow:
1. enqueue command
2. worker consumes command
3. writes job status/history to S3
4. `/info` shows recent/latest job state

## Standard runtime modes
Supported standard runtime modes:
- `timer`
- `sync-only`
- `render_v2`
- `reminder_v2`
- `reminders-only`
- `morning`
- `test`

Unsupported legacy planner modes are intentionally rejected.

## Entry boundary rules
- `index.py` must remain thin.
- `index.py` and `src/entrypoints/runtime/planner_runtime_entry.py` must stay import-safe and construct `AppContext` only inside explicit runtime/factory calls.
- `src/entrypoints/**` owns transport parsing/translation only.
- domain logic lives in `src/core/**` and focused service/use-case modules.
- archived planner/bootstrap/render/reference code lives under `src/legacy/**` and must not be imported by standard runtime.
- browser-facing access policy belongs at the HTTP/access boundary, not inside query engine internals.

## Browser-facing access contract

Canonical browser-facing data/auth namespaces:
- prod API: `/ops/api/*`
- test API: `/test/ops/api/*`
- prod auth: `/ops/auth/*`
- test auth: `/test/ops/auth/*`
- shared infra route: `/grafana/*`

The active backend direction is:
- one canonical frontend payload path,
- one canonical read-side query path,
- optional masking as a post-build transform,
- no separate masked query engine.
- trusted `x-dtm-*` handling is constrained by [auth_trust_boundary.md](/n:/PROJECTS/python/SCRIPT/DTM/docs/system/auth_trust_boundary.md).

## Storage roles
- Object Storage/S3:
  - raw snapshot
  - prep snapshot
  - people snapshot
  - extra metadata
  - job status/history
  - attachment binaries
- Yandex Message Queue:
  - async command intake
- YDB:
  - no longer canonical for API v2 runtime path
  - remaining code is legacy/reference or non-canonical support debt
