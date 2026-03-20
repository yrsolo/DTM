# Access API

## Purpose

`access_api` owns:
- frontend-facing HTTP read surface
- access/auth interpretation at the backend boundary
- masked/open response policy
- browser-safe DTO assembly
- cached primary task-list delivery, including card data and attachment visibility in the browser payload

## Public facade expectation

Target context shape:

```text
src/contexts/access_api/
  public.py
  module.py
  contracts/
  application/
  domain/
  adapters/
```

## Allowed dependencies

- `snapshot.public` or other public context contracts needed to assemble browser-safe payloads
- access/masking logic owned by the context
- platform/entrypoint transport shells delegating into the context facade
- runtime-owned invalidation/read-freshness signals where the primary read-model scenario depends on them

## Forbidden dependencies

- direct dependence on worker/runtime details
- direct imports into snapshot/rendering/attachments internals
- browser-facing behavior hidden inside transport router code

## Commands owned

- no primary queue commands are expected here as the ownership center

## Routes owned

- frontend/public API routes
- masked/open access read surface

## Transitional extraction notes

- owning handler implementation now lives under `src/contexts/access_api/internal/*`
- `src/contexts/access_api/module.py` builds frontend root, frontend v2, info, people snapshot, and attachment read handlers from the context-owned internal package
- legacy HTTP handler wrappers have been removed; `src/entrypoints/http/*` remains transport-only and delegates through the access-api public facade
- remaining extraction target is thinner transport parsing and response translation around the already-moved access-api ownership center
- in the primary read-model scenario, `access_api` is the browser-facing finish line: attachment is considered delivered only when it appears in the cached main browser payload
