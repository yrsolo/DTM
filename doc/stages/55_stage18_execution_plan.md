# Stage 18 Execution Plan

## Objective
Harden multi-LLM runtime reliability with explicit timeout/retry guardrails and provider-level enhancer counters.

## Baseline
- Stage 18 estimate baseline: 5 tasks.
- Dynamic tracking rule: after each completed task update `Done` and `Remaining` in `agile/sprint_current.md`.
- Current counter: done `5`, remaining `0`.

## Stage 18 slices
1. `DTM-182`: kickoff and bounded queue.
2. `DTM-183`: runtime reliability guardrails and enhancer counters.
3. `DTM-184`: smoke coverage for reliability contour.
4. `DTM-185`: docs and tracking refresh.
5. `DTM-186`: closeout and Stage 19 handoff.

## Exit criteria
- Provider adapters run with configurable timeout and transient retry.
- Quality report includes enhancer counters and provider identity.
- Deterministic smoke checks pass locally.
