# CAM-2026-03-12-DIRECT-API-OUTER-LATENCY-DECOMPOSITION-V1 Charter

## Problem
- direct `/api` frontend requests still show multi-second wall clock on `test`
- current frontend inner stage traces show only about `130 ms` on cache-hit path
- remaining latency is not localized inside current backend instrumentation

## Goal
- decompose direct `/api` latency at the outer function boundary
- expose debug-only timing through headers and `/info`
- determine whether the remaining delay is inside function wrapper code or outside the function entirely

## Non-goals
- no `bff` work in this campaign
- no direct optimization of latency yet
- no payload contract changes for `/api/v2/frontend`

## Exit Criteria
- direct `/api` emits outer timing metrics and debug headers when profiling is enabled
- `/info` detail shows recent direct `/api` outer traces and summary values
- live `test` evidence compares client wall clock vs function/shell/handler/inner totals
- evidence states whether the unexplained gap is inside the function or outside it
