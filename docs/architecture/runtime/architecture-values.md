# Architecture Values

This document is normative for architecture decisions in this repository.

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

### Planner-centric runtime is transitional
- `planner_runtime_entry.py` may exist as compatibility adapter
- it must not remain the conceptual center of the system

### Bootstrap is composition root only
- bootstrap loads config, wires dependencies, and assembles context
- bootstrap must not execute business logic
- bootstrap must not create global runtime state at import time

### Import-time side effects are a bug
- no module-level production `AppContext` construction in active runtime entry modules
- active modules must be importable in tests without production env and cloud credentials

### Observability is mandatory but hot-path safe
- metrics/logs/job status remain required
- hot paths must avoid uncontrolled synchronous metric spam
- default user paths must avoid heavy diagnostics by default

### Telegram/reminder is frozen
- keep it operational if needed
- do not use it as the model for new architecture during this wave
- do not spend primary effort on redesign there unless break/fix is required

## Boundary guidance

Canonical active areas:
- `src/snapshot_engine/*`
- `src/entrypoints/http/*`
- `src/jobs/*`
- `src/worker/*`
- `src/commands/*`
- `src/observability/*`

Transitional areas:
- `src/entrypoints/runtime/planner_runtime_entry.py`
- old root `core/*`
- legacy compatibility helpers still pulled by active runtime

Frozen-but-not-target areas:
- `src/telegram/*`
- `src/notify/*`
