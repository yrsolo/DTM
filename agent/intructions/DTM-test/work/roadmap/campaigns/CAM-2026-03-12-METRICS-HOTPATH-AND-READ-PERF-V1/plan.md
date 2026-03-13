# CAM-2026-03-12-METRICS-HOTPATH-AND-READ-PERF-V1

Status: planned
Priority: P0
Owner intent: make refresh and frontend/API performance evidence-driven, reduce instrumentation overhead, and prepare fast path for common frontend requests.

## Problem statement

Observed facts:
- snapshot refresh business time appears around ~5s in metrics
- user-visible refresh timing on info page is around ~20s
- API requests are often ~1-2s, acceptable but slower than desired

Strong suspects:
- queue lag / worker startup overhead
- sync metric emission in hot path
- dual-write metric backends
- expensive default info page sections
- no prebuilt hot response for common frontend query

## Scope

In scope:
- `src/observability/*`
- `src/jobs/update_snapshot_job.py`
- `src/worker/worker.py`
- `src/entrypoints/http/http_shell.py`
- `src/entrypoints/http/info_handler.py`
- frontend read payload build path
- optional hot cache for default frontend request

Out of scope:
- Telegram/reminder optimizations beyond preserving frozen behavior
- major UI redesign

## Required deliverables

1. Stage-level metrics for refresh wall-clock decomposition.
2. Evidence on metrics emission overhead.
3. Reduced sync metric overhead on hot paths.
4. Lightweight default `/info` path.
5. Proposal or implementation for prebuilt cache of common frontend request.

## Required stage timings

### Refresh flow

Measure separately:
- command accepted time
- enqueue latency
- dequeue latency
- worker bootstrap/setup latency
- snapshot raw build latency
- prep build latency
- status store write latency
- metrics flush latency
- total wall-clock until user-visible status changes

### HTTP/frontend flow

Measure separately:
- request parse
- access context resolve
- query execution / payload build
- masking transform
- metrics/log emission
- response serialization
- total response time

## Strong design recommendations

### 1. Stop paying per-metric network cost in hot HTTP path

If `HttpShell` writes metrics directly to sync backends, refactor toward request-scoped batch collector and a controlled flush strategy.

### 2. Do not flush twice just to record flush metrics

If there is a flush-of-flush pattern, remove or isolate it so that recording flush latency does not cause another expensive flush cycle.

### 3. Make `/info` cheap by default

Heavy diagnostics such as object-storage scans must move to explicit detail mode.

Suggested contract:

```python
class InfoHandler:
    def handle(self, event: dict) -> dict: ...
    def _summary_payload(self) -> dict: ...
    def _detail_payload(self) -> dict: ...
```

Default route should serve summary payload only.

### 4. Add optional prebuilt cache for common frontend request

Suggested seam:

```python
class FrontendHotCache:
    def get(self, key: str) -> dict | None: ...
    def put(self, key: str, payload: dict) -> None: ...

class FrontendCacheKeyBuilder:
    def default_full(self, contour: str) -> str: ...
    def default_masked(self, contour: str) -> str: ...
```

Initial scope may cover only default frontend v2 query for:
- prod full
- prod masked
- test full
- test masked

## Concrete tasks

1. Audit current metric backend wiring and whether both Monitoring and Prometheus are written on hot paths.
2. Add stage timings for refresh lifecycle.
3. Add stage timings for frontend/API lifecycle.
4. Measure metric flush overhead explicitly.
5. Refactor HTTP metrics emission to batching/deferred flush where safe.
6. Remove redundant flush-of-flush pattern.
7. Split `/info` into summary vs detail.
8. Measure default frontend request and identify dominant sub-stages.
9. Add or design hot cache for most common frontend request.
10. Produce before/after evidence.

## Acceptance criteria

- evidence clearly explains difference between ~5s business refresh and ~20s visible refresh
- sync metric overhead is quantified
- default `/info` route is lighter and separately timed from detail diagnostics
- frontend/API stage timings exist
- hot cache decision is documented and ideally implemented for default request
