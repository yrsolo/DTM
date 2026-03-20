# Architecture Values

This document is normative for architecture decisions in this repository.

For active architecture work, read this together with:
- [../module-first-recovery/README.md](../module-first-recovery/README.md)

## Purpose

This file defines the architectural values and target shape of DTM for active design and implementation decisions.

When code, docs, or agent proposals conflict with this file, this file wins unless the owner explicitly overrides it in the current chat.

## Core direction

DTM is a snapshot-first, queue-backed, browser-safe, serverless read platform.

Target formula:
- thin entrypoints
- use-case oriented orchestration
- snapshot/query layer for reads
- adapters at the edges

## Non-negotiable values

### Read path is cache-only
- read endpoints must not read Google Sheets directly
- read endpoints must not perform expensive rebuilds
- read endpoints must not execute render/notify/update side effects
- read endpoints read from prepared snapshot/query/cache layers and lightweight operational stores

### One read model, one query engine
- one canonical read side
- one canonical frontend payload builder
- no separate masked query engine
- no feature-specific mini query engines

### Browser auth stays at the boundary
- auth proxy decides full vs masked
- backend resolves access context at the boundary
- backend builds one canonical payload shape
- masking is post-build transform only

### Deterministic masking only
- masking must be deterministic
- masking must preserve payload shape
- same real entity maps to the same fake value for the same dictionary version

### Planner-centric runtime is not the conceptual center
- `planner_runtime_entry.py` may exist as a local/manual runtime bridge
- it must not become the conceptual center of the system

### Bootstrap is composition root only
- bootstrap loads config, wires dependencies, and assembles context
- bootstrap must not execute business logic
- bootstrap must not create global runtime state at import time
- bootstrap may delegate only and must not become the new central ownership layer

### Import-time side effects are a bug
- no module-level production `AppContext` construction in active runtime entry modules
- active modules must be importable in tests without production env and cloud credentials

### Observability is mandatory but hot-path safe
- metrics/logs/job status remain required
- hot paths must avoid uncontrolled synchronous metric spam
- default user paths must avoid heavy diagnostics by default

### Context-first extraction is now the active path
- `attachments`, `reminders`, `snapshot`, `rendering`, `telegram_interaction`, and `access_api` are first-class contexts for active work
- ownership sits behind `src/contexts/*`
- new work should reinforce context facades and boundaries, not reopen transport-first or adapter-first ownership

## Boundary guidance

Canonical active areas:
- `src/contexts/*`
- `src/platform/*`
- `src/entrypoint/*`
- `src/contexts/snapshot/internal/engine/*`
- `src/entrypoints/http/*`
- `src/worker/*`
- `src/commands/*`
- `src/observability/*`

Supporting areas:
- `src/entrypoints/runtime/planner_runtime_entry.py`
- `src/core/*`
- archive and historical reference material outside the active path

## Refactor governance note

- `docs/architecture/module-first-recovery/README.md` is the master text for active architecture decisions
- child campaigns should refresh trust against current code before decomposition
