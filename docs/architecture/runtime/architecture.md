# Architecture (Current)

## Purpose

DTM is a snapshot-first, queue-backed, browser-safe serverless runtime.

Canonical formula:
- Google Sheets as source input,
- Raw/Prep snapshots in Object Storage,
- browser/API reads from prepared snapshots,
- heavy mutations through queue-backed jobs,
- browser auth and masking enforced at the HTTP boundary.

Governing policy:
- [architecture-values.md](architecture-values.md)

## Canonical runtime contour

1. Fetch Sheets data (`values + colors`)
2. Normalize into canonical task state
3. Write Raw snapshot
4. Merge extra metadata and build Prep snapshot
5. Serve/query/render/notify from Prep snapshot and related lightweight stores

Primary consumers:
- `/api/v2/frontend`
- `/info`
- render jobs
- reminder jobs
- group-query reply jobs

## Runtime topology

- `index.py` is the thin top-level shell
- transport shells handle:
  - HTTP
  - queue worker events
  - scheduled triggers
  - explicit runtime-mode execution

## Browser-facing boundary

Canonical browser-facing namespaces:
- prod API: `/ops/api/*`
- test API: `/test/ops/api/*`
- prod auth: `/ops/auth/*`
- test auth: `/test/ops/auth/*`
- shared infra route: `/grafana/*`

Boundary ownership:
- external auth contour/function owns auth/session routes and callbacks
- this repo owns browser data routes and validates trusted ingress before honoring `x-dtm-*`

Current backend direction:
- one canonical frontend payload path
- one canonical query path over prep snapshot
- optional masking as a post-build transform
- no separate masked query engine

Operator-facing auth details:
- [../../integrations/browser-auth/runbook.md](../../integrations/browser-auth/runbook.md)
- [../../integrations/browser-auth/trust-boundary.md](../../integrations/browser-auth/trust-boundary.md)

## Async mutation contour

Heavy or mutating actions are queue-backed:
- snapshot refresh
- timeline render
- designers render
- reminders
- attachment metadata update
- group query reply

Flow:
1. validate/build internal command
2. enqueue command
3. worker executes one job
4. job status/history is written to Object Storage
5. `/info` exposes recent/latest state

## Runtime boundaries

- `index.py` remains thin and import-safe
- `src/entrypoints/**` owns transport parsing/translation only
- `src/contexts/snapshot/internal/engine/*` owns read-side build/query/storage logic
- context-owned jobs and `src/worker/*` own mutation execution
- browser access policy stays at the HTTP boundary, not inside query internals
- render/notify/group-query consume prepared snapshot data instead of inventing parallel read contours

## Storage roles

- Object Storage/S3:
  - raw snapshot
  - prep snapshot
  - people snapshot
  - extra metadata
  - response-cache objects
  - job status/history
  - attachments
- Yandex Message Queue:
  - async command intake

## Current non-goals for active docs

The current architecture story does not treat the following as canonical runtime contours:
- planner-era orchestration as the conceptual center
- legacy database/readmodel source paths
- historical migration/cutover plans

If historical detail is needed, use `docs/archive/*`.

## People registry distinction
- `/api/v2/people` is a secret-only internal auth-support route over the canonical people snapshot.
- `frontend_v2.entities.people` is a derived owner list from selected tasks.
- people snapshot is the canonical registry for reminder/auth lookup and internal reads.
- people registry explicitly separates `contactEmail` from `yandexEmail` so auth/account identity is not mixed with human-contact data.
- the HTTP API exposes a clean projection of that registry, not the raw mapped row payload.
