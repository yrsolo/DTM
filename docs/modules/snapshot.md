# Snapshot

## Purpose

`snapshot` owns:
- ingestion
- normalization
- state build/update
- prepared read-side state and public query-facing contracts
- projection of attachment state into the primary task-list read-model

## Public facade expectation

Target context shape:

```text
src/contexts/snapshot/
  public.py
  module.py
  contracts/
  application/
  domain/
  adapters/
```

## Allowed dependencies

- source adapters needed for ingestion
- persistence/query adapters owned by the context
- domain normalization code and state models

## Forbidden dependencies

- rendering reaching directly into snapshot internals
- transport/runtime ownership of snapshot business rules
- direct env/config access outside approved config/bootstrap layers

## Commands owned

- `update_snapshot`

## Routes owned

- no primary frontend route ownership is expected here
- snapshot exposes public contracts/facades for other contexts, especially `access_api` and `rendering`

For the primary read scenario, `snapshot` is the point where mutation-state becomes visible read-side state in the main browser payload.

## Current implementation notes

- current implementation spans `src/core/*`, `src/contexts/snapshot/adapters/sources/*`, `src/contexts/snapshot/internal/engine/*`, and snapshot job wiring
- the old top-level `src/snapshot_engine/*` root is removed; the read-side engine now lives physically inside the snapshot context
