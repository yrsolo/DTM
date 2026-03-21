# CAM-2026-03-21-SNAPSHOT-MODULE-SURFACE-V1

## Why

`contexts/snapshot` is physically internalized, but the active module surface still reads mainly through:

- `build_snapshot_engine`
- `module.engine(ctx)`
- thin capability proxies bound to that engine

That means `snapshot` still feels like a wrapped engine center rather than a standalone module-first surface.

## Smell

`snapshot` is still engine-centric instead of contract-first.

## Target Ideal

The snapshot scenario is read as:

- `contexts.snapshot.public`
- `contexts.snapshot.module`
- query/update/attachment projection capabilities as first-class module contracts
- engine only as an internal implementation detail

## Kill Criteria

1. `SnapshotModule` no longer centers its public meaning on `engine()`
2. exported capabilities read as real module contracts, not thin engine proxies
3. public grammar stops exposing convenience wrappers that exist only because `engine` is the center
4. snapshot behavior and current read/update tests remain stable

## Scope Boundary

- `src/contexts/snapshot/public.py`
- `src/contexts/snapshot/module.py`
- `src/contexts/snapshot/application/*` as needed
- `src/contexts/snapshot/internal/engine/*` only if required by the first contract cut
- affected snapshot tests

## Non-Goals

- no payload/schema changes
- no storage/layout rewrite
- no cross-context API redesign beyond the first snapshot contract cut
