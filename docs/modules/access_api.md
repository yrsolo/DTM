# Access API

## Purpose

`access_api` owns:
- frontend-facing HTTP read surface
- access/auth interpretation at the backend boundary
- masked/open response policy
- browser-safe DTO assembly

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

- current implementation is spread across frontend handlers, access masking, and frontend query adapters
- the extraction target is one clean browser-facing context, not a transport folder with scattered policy

