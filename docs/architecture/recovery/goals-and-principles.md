# Goals And Principles

## What this program is fixing

The main problem is no longer missing layers or missing docs.

The main problem is that the code still reads through technical clusters:
- `entrypoints`
- `jobs`
- `services`
- `render`
- `notify`
- `telegram`
- `snapshot_engine`

Instead of reading through owning modules:
- `entrypoint`
- `platform.runtime`
- `snapshot`
- `rendering`
- `reminders`
- `attachments`
- `telegram_interaction`
- `access_api`

## Target state

DTM must become a module-first system:
- one short top path
- one neutral runtime layer
- one obvious owning module for each scenario
- module communication only through narrow public surfaces, contracts, commands, queries, intents, or runtime-owned orchestration

## Core principles

### Module first
The architectural unit is the module, not the handler, services package, worker, or adapter cluster.

### Runtime is neutral
`platform.runtime` may classify, dispatch, orchestrate, and expose diagnostics.
It must not own business rules.

### One obvious path
Each active scenario must read as:
- entrypoint
- runtime routing
- owning module public facade
- module-local builder or use case

### No deep cross-module knowledge
Allowed cross-module access:
- `public.py`
- `contracts`
- explicit internal commands, queries, or intents

### Cache is not domain glue
Mutations must not directly couple modules through frontend-cache helper calls.
Cache aftermath must go through runtime-owned invalidation intents or jobs.

### Old path must die
A new path is not considered adopted until at least one competing old path is removed, banned, or hard-deprecated with a removal task.
