# Rendering

## Purpose

`rendering` owns:
- timeline rendering
- designers rendering
- representation/writeback use-cases

It does not own snapshot ingestion or snapshot internal state assembly.

## Public facade expectation

Target context shape:

```text
src/contexts/rendering/
  public.py
  module.py
  contracts/
  application/
  domain/
  adapters/
```

## Allowed dependencies

- sheet/render adapters owned by the context
- `snapshot.public` facade
- snapshot contracts explicitly intended for rendering inputs

## Forbidden dependencies

- direct imports into snapshot internals
- direct dependence on snapshot private builders or internal storage details
- business rules living in trigger/runtime/worker shells

## Commands owned

- `render_timeline_sheet`
- `render_designers_sheet`

## Routes owned

- no primary HTTP route ownership is expected here
- rendering is primarily a command-driven context in this wave

## Transitional extraction notes

- current rendering logic is split across `src/render/*`, render jobs, and snapshot-engine-coupled code
- the hard anti-corruption boundary is mandatory:
  - `rendering` depends only on `snapshot.public` or snapshot contracts
  - direct snapshot-internal imports from rendering are forbidden

