# DTM Architecture Values

Status: active
Last updated: 2026-03-12
Owner intent: current source of truth for architecture direction.

## Purpose

This document defines the architectural values and target shape of DTM. It is not a historical document. It exists to prevent drift back into planner-centric, hybrid, opaque runtime patterns.

When code, docs, or agent proposals conflict with this file, this file wins unless the owner explicitly overrides it.

---

## 1. What DTM is becoming

DTM is a **snapshot-first, queue-backed, browser-safe, serverless read platform** built around Google Sheets as source-of-truth for core task data and ExtraStore as source-of-truth for attached/user-enriched data.

Target formula:

`thin entrypoints -> use-cases -> snapshot/query layer -> adapters at edges`

Target runtime formula:

- sync read path from prepared cache
- async command path through queue
- explicit job execution in worker
- observability everywhere
- browser auth/masking outside domain query logic

---

## 2. Non-negotiable values

### 2.1 Read path is cache-only

Read endpoints must not:
- read Google Sheets directly,
- perform expensive rebuilds,
- execute planner-like orchestration,
- run render/notify/update side effects.

Read endpoints must read from:
- `PrepCache`
- `SnapshotEngine`
- lightweight operational status stores
- prebuilt hot caches where explicitly allowed.

### 2.2 One read model, one query engine

There must be a single canonical read side.

Allowed:
- one `SnapshotQueryEngine`
- one canonical frontend payload builder
- optional derived hot caches for common requests

Forbidden:
- separate business query logic for API vs frontend vs masked mode
- feature-specific mini query engines
- planner-style branching trees inside read handlers

### 2.3 Extra data stays separate from sheet truth

Core fields from Sheets and additional user data have different truth boundaries.

- Sheets = source of truth for core task fields
- ExtraStore = source of truth for attachments, notes, added metadata, future enrichment

Merge must be explicit.

### 2.4 Web/browser auth must not fork domain logic

Browser auth and masking are transport/access concerns.

Required pattern:
- auth proxy determines full vs masked
- backend builds one canonical payload shape
- `MaskingTransformer` rewrites sensitive display fields only

Forbidden:
- separate masked query logic
- access checks scattered deep inside domain filtering
- browser-supplied `x-dtm-*` headers trusted directly outside trusted proxy chain

### 2.5 Deterministic masking, not random masking

Masked mode must be:
- deterministic,
- shape-preserving,
- stable across repeated requests,
- fast.

Same real entity should map to same fake entity for the same dictionary version.

### 2.6 Planner-centric runtime must die out

`planner_runtime_entry.py` may exist temporarily as a compatibility adapter, but must not remain the conceptual center of the system.

Target orchestration is use-case based, not planner based.

### 2.7 Bootstrap is composition root only

Bootstrap may:
- load typed config,
- wire dependencies,
- choose implementations,
- assemble app context.

Bootstrap must not:
- execute business logic,
- create global runtime state at import time,
- be required to import arbitrary modules in tests.

### 2.8 Import-time side effects are a bug

No global `APP_CONTEXT = build_app_context()` in active runtime modules.

Modules must be importable in tests without production env, cloud credentials, or external service availability.

### 2.9 Two-domain-world drift must be removed

The project must converge on canonical `src/*` runtime modules.

Legacy `core/*`, planner-era imports, and compat helpers may temporarily exist but are not target architecture.

### 2.10 Observability is mandatory, but hot-path safe

Metrics, logs, and job status are required.

But observability must not dominate wall-clock time of hot paths.

Required direction:
- stage-level timings
- structured logs
- async-or-batched metric emission where possible
- evidence-driven tuning

Forbidden:
- uncontrolled synchronous dual-write metric spam in hot path
- deep logging of giant payloads
- heavy diagnostics on default user paths

---

## 3. Architectural style we are intentionally moving toward

DTM intentionally combines:

- **Clean Architecture**
- **Ports and Adapters / Hexagonal**
- **DDD-lite**
- **CQRS-style read model separation**
- **Queue-backed command processing**
- **Serverless cloud-native runtime**

This does **not** mean over-engineering.

DTM is not trying to become a framework. It is trying to become a clean, observable, reliable product runtime.

---

## 4. Freeze policy

Telegram/reminder is currently in **architecture freeze**.

Meaning:
- keep it operational if needed,
- do not use it as the model for new architecture,
- do not spend primary effort polishing it now,
- after runtime/core/read/auth cleanup, rewrite it to new standards.

This freeze applies to:
- webhook refinements
- reminder flow refinements
- group query refinements

unless required for break/fix production safety.

---

## 5. Performance values

### 5.1 Snapshot refresh

Business refresh duration and wall-clock user-visible refresh duration are different metrics and both matter.

We optimize for:
- low business execution time
- low queue-to-visible latency
- low instrumentation overhead
- low info/admin page latency

### 5.2 API/read path

Goal direction:
- default frontend request should be served from prepared cache
- common request paths may have prebuilt hot cache
- masking must be cheap enough to avoid becoming dominant cost

### 5.3 Info/admin pages

Default info/admin views must be lightweight.
Heavy diagnostics must be optional, explicit, and separately timed.

---

## 6. Required source priorities for agents

When planning or implementing work, the trust order is:

1. owner instruction in current chat
2. this file
3. active campaign docs in `work/roadmap/campaigns/*`
4. verified code paths
5. older system docs
6. archived campaign docs

If README or historical docs conflict with code and active campaign docs, agents must treat them as stale until verified.

---

## 7. Canonical boundaries

### Canonical read-side modules

- `src/snapshot_engine/*`
- `src/entrypoints/http/*`
- `src/jobs/*`
- `src/worker/*`
- `src/commands/*`
- `src/observability/*`

### Transitional modules

- `src/entrypoints/runtime/planner_runtime_entry.py`
- old root `core/*`
- legacy/compat builders still pulled by active runtime

### Frozen-but-not-target modules

- `src/telegram/*`
- `src/notify/*`

---

## 8. Hard bans for new work

Do not introduce new code that:
- adds more planner-centric orchestration,
- adds import-time bootstrap side effects,
- adds new `core/*` dependencies into new `src/*` modules,
- duplicates selection logic,
- mixes masked/full data access inside query engine internals,
- adds heavy sync metric writes inside hot path without evidence,
- makes info/admin default responses more expensive.

---

## 9. Desired end-state in one paragraph

DTM should end up as a serverless, queue-backed, snapshot-first system where browser traffic goes through auth proxy, read APIs answer from prepared caches, common frontend payloads are fast and optionally prebuilt, full and masked access share one payload contract, async jobs are explicit and idempotent, metrics are stage-granular but efficient, and the runtime no longer depends conceptually on planner-era orchestration.
