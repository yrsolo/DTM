# Modularity Audit 2026-03-19

This audit evaluates how close the active DTM runtime is to the intended modular-monolith shape after the refactor umbrella campaign.

Assessment method:
- verify the current context/public/module surfaces in `src/contexts/*`
- verify current active cross-layer imports in `src/contexts`, `src/entrypoints`, `src/jobs`, `src/render`, `src/notify`, `src/entrypoints_adapters`, `src/services`
- compare the code against the target stated in `modular-monolith-v2.md` and `module-map.md`

Important framing:
- this is an architectural readiness audit, not a bug report
- scores below measure module autonomy, not code quality
- a module may be cleanly owned but still not be service-extraction-ready

## Executive summary

Overall result:
- structural modularity: good
- runtime independence between modules: medium
- service-extraction readiness: medium-low

The refactor clearly improved the system:
- active runtime no longer depends on `src.legacy`
- top-level routing and queue orchestration are explicit
- first-class context facades exist
- snapshot boundary rules for rendering/notify/adapters are enforced by tests

But the system is still not a set of near-independent modules.

The main reason is that `snapshot` still acts as a shared backbone rather than just another peer context. Most other modules remain dependent on snapshot-owned read-side state and, in several places, still delegate into older implementation clusters such as `src/render`, `src/notify`, `src/telegram`, `src/services/attachments`, and `src/entrypoints/http`.

## Readiness scale

- `8-10`: good candidate for independent extraction; clear facade, narrow contracts, low implementation leakage
- `5-7`: acceptable modular-monolith context, but still tied to shared implementation or broad contracts
- `0-4`: mainly an ownership wrapper over older code; not independently evolvable yet

## Module scorecard

| Module | Readiness | Current state | Main blockers |
|---|---:|---|---|
| `attachments` | 7/10 | best extracted context | still depends on snapshot engine and HTTP/cache implementation details |
| `reminders` | 5/10 | ownership established, implementation still old-cluster-backed | uses `src.notify/*`, provider wiring, and shared snapshot engine |
| `rendering` | 5/10 | boundary improved, ownership visible | implementation still lives in `src/render/*`, broad dependency on snapshot |
| `telegram_interaction` | 4/10 | command/webhook ownership is clearer | strongly coupled to `src.telegram/*`, `src.notify/*`, and snapshot-backed reminder use case |
| `access_api` | 3/10 | mostly a facade over HTTP handlers | context delegates straight back into `src.entrypoints/http/*` |
| `snapshot` | 6/10 | canonical shared read-side owner | too central and too broad; exports engine-style capability rather than narrow contracts |

## Detailed findings

### `attachments` - 7/10

What is good:
- clear context surface in `src/contexts/attachments/public.py`
- commands are clearly owned by the context
- jobs already route through the context facade
- this is the closest module to a real bounded application slice

What still couples it:
- `src/contexts/attachments/module.py` still asks snapshot for a full engine via `get_snapshot_engine`
- attachment jobs still invalidate frontend cache through `src/entrypoints/http/frontend_response_cache.py`
- implementation lives in `src/services/attachments/*`, which is still an old shared application area rather than a context-internal package

What to do next:
1. replace `get_attachment_snapshot_engine()` with narrower attachment-facing snapshot capabilities:
   - metadata publication
   - attachment read projection access
2. move cache invalidation behind an access-api or snapshot-read facade instead of importing HTTP cache helpers from jobs
3. migrate `src/services/attachments/*` under `src/contexts/attachments/`

### `reminders` - 5/10

What is good:
- context facade exists and jobs route through it
- ownership is now explicit in runtime/trigger routing

What still couples it:
- `src/contexts/reminders/module.py` still builds directly from `src.notify`
- the module owns provider wiring, formatter wiring, sender wiring, and snapshot access all in one builder
- reminder use cases still consume a broad snapshot-engine-backed dependency

What to do next:
1. split the module into internal slices:
   - selection/use-case
   - formatting
   - delivery
   - optional LLM enhancement
2. replace engine-style snapshot dependency with reminder-specific read contracts
3. move `src.notify/*` into context-internal packages under `src/contexts/reminders/`

### `rendering` - 5/10

What is good:
- anti-corruption boundary to snapshot is now real and test-enforced
- rendering jobs route through the context
- target validation is explicit and separated

What still couples it:
- `src/contexts/rendering/module.py` still depends on `src.render`
- the module returns old render use cases, jobs, requests, and writer types almost unchanged
- rendering still depends on broad snapshot contracts and engine-backed querying

What to do next:
1. move `src/render/*` under `src/contexts/rendering/`
2. define rendering-owned request/result contracts instead of re-exporting legacy render types
3. narrow snapshot interaction to rendering-specific query contracts:
   - tasks in window
   - designer assignment projection
   - render-safe state version/freshness info

### `telegram_interaction` - 4/10

What is good:
- webhook and `group_query_reply` ownership is finally explicit
- public facade exists

What still couples it:
- `src/contexts/telegram_interaction/module.py` is effectively a wrapper over `src.telegram/*`
- it also reaches into `src.notify` to reuse reminder use case and formatter-related behavior
- group-query still behaves like a reminder-adjacent feature, not a fully self-contained Telegram interaction slice

What to do next:
1. move `src.telegram/*` under `src/contexts/telegram_interaction/`
2. split `group_query` from reminder internals through a dedicated query/use-case contract
3. define one Telegram interaction application layer that owns:
   - update parsing
   - command routing
   - sender
   - group-query reply flow

### `access_api` - 3/10

What is good:
- context ownership exists on paper
- router now depends on context facade instead of directly constructing everything itself

What still couples it:
- `src/contexts/access_api/module.py` directly returns handlers from `src/entrypoints/http/*`
- this is still transport-first implementation with ownership labels added on top
- read-side policies such as caching, masking, and access context still live in HTTP-layer packages

What to do next:
1. move handler-independent read policy into `src/contexts/access_api/`
2. keep only transport parsing/response translation in `src/entrypoints/http/*`
3. convert handlers into thin shells over access-api use cases rather than treating handlers themselves as the module

### `snapshot` - 6/10

What is good:
- snapshot is clearly recognized as the canonical read-side owner
- external code now depends on `snapshot.public` and `snapshot.contracts` rather than direct imports into `src.snapshot_engine`
- this was the most important structural win of the refactor

What still couples it:
- `src/contexts/snapshot/module.py` is still mostly a bridge to `src.snapshot_engine`
- `snapshot.public` exposes `get_snapshot_engine()`, which leaks a broad dependency shape outward
- `snapshot.contracts` still re-export types straight from `src.snapshot_engine.model`
- snapshot remains a central backbone for almost every other context

What to do next:
1. stop exposing `get_snapshot_engine()` to external contexts
2. replace engine access with capability-oriented snapshot APIs:
   - frontend query
   - people query
   - prep/raw access where truly needed
   - attachment metadata projection
   - reminder/render query contracts
3. move `src.snapshot_engine` inward conceptually and treat it as implementation detail of the snapshot context

## Cross-cutting coupling hotspots

These are the biggest remaining sources of system-wide coupling.

### 1. Snapshot as a broad shared backbone

This is the biggest remaining architectural coupling.

Symptoms:
- multiple contexts still ask snapshot for a full engine or engine-shaped dependency
- contracts are still derived from `src.snapshot_engine.model`
- snapshot is both a context and an implementation backbone

Recommended next move:
- make `snapshot.public` capability-oriented
- forbid new uses of `get_snapshot_engine()` outside the snapshot context

### 2. Transitional implementation clusters remain outside contexts

Still-active clusters:
- `src/render/*`
- `src/notify/*`
- `src/telegram/*`
- `src/services/attachments/*`
- parts of `src/entrypoints/http/*`

Recommended next move:
- migrate each cluster under its owning context
- leave compatibility re-exports only if needed temporarily

### 3. Access API is not yet a real business module

Right now it is mostly a context label over HTTP handlers.

Recommended next move:
- pull masking, caching, trusted/untrusted shaping, and attachment read policy behind access-api application services
- reduce handlers to transport-only shells

### 4. Bootstrap still knows too much

The system is much better than before, but the composition root is still highly important to all active slices.

Recommended next move:
- move more assembly into context-local builders
- keep bootstrap only as delegation glue

## Suggested decoupling plan

Priority order for the next waves:

1. `snapshot` capability split
- replace broad engine exposure with narrow read contracts
- this gives the biggest independence gain across the whole system

2. `access_api` extraction for real
- separate transport from access-policy/read-shaping logic
- this removes HTTP-layer leakage into jobs and context composition

3. `attachments` internal consolidation
- move `src/services/attachments/*` under the context
- remove direct dependency on HTTP cache helpers

4. `rendering` internal consolidation
- move `src/render/*` into the context
- replace render-legacy DTO exposure with context-owned contracts

5. `reminders` and `telegram_interaction` split by behavior
- stop sharing reminder-centric internals for group-query and Telegram flows
- give each context its own internal application surface

## Bottom line

The megaplanned refactor worked, but it delivered phase-one modularity, not final modular independence.

The repo is no longer an unstructured monolith.
It is now a guarded modular monolith with real ownership surfaces.

That said, it is still too coupled to claim that the system is already decomposed into independently evolvable modules.

The main unfinished work is not top-level routing anymore.
It is moving implementation ownership inward and replacing broad shared dependencies with narrower context-specific capabilities.
