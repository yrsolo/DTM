# CAM-2026-03-12-METRICS-HOTPATH-AND-READ-PERF-V1

## Goal

Make refresh and frontend/API performance evidence-driven, reduce instrumentation overhead, and harden the read path, including mandatory `/info` summary/detail separation.

## Scope

In scope:
- `src/observability/*`
- refresh/worker timing path
- `src/entrypoints/http/info_handler.py`
- frontend/default read payload build path
- optional hot cache for common frontend request

Out of scope:
- Telegram/reminder redesign
- cosmetic frontend work

## Concrete tasks

1. Verify current metrics write/flush path and hot-path cost.
2. Add wall-clock stage timings for refresh and frontend/API lifecycle.
3. Split `/info` into cheap default summary and explicit detail diagnostics as a required deliverable.
4. Measure dominant read-path stages and masking-ready hotspots.
5. Decide and, if justified, implement default hot cache seam for common frontend request.

## `/info` contract

- default `/info` returns lightweight summary only
- heavy diagnostics are available only in explicit detail mode
- allowed forms:
  - `/info?view=detail`
  - `/info/detail`
- summary must not:
  - perform heavy storage scan
  - build expensive aggregates
  - read large blobs or full indexes
- detail may be slower, but must be explicitly separated

## Acceptance criteria

- evidence explains business refresh time vs visible wall-clock gap
- sync metrics overhead is quantified
- typical summary `/info` is measurably faster than current baseline
- default `/info` path is lighter than detail mode
- metrics include separate `info.summary.ms` and `info.detail.ms`
- frontend/API stage timings exist
- hot cache decision is documented with evidence
