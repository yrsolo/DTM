# CAM-GROUP-QUERY-UNIFY-WITH-REMINDER-V1

## Goal

Make group query a specialization of the reminder selection path instead of a separate mini-domain.

## Scope

- unify task selection logic with reminder selection
- remove `pandas` from group query handler
- introduce dedicated group-query formatter
- keep rollout decision about sync vs async explicit

## Non-goals

- no Telegram webhook platform rollout here
- no queue requirement in first implementation step unless explicitly chosen

## Implementation Skeleton Reference

- Primary implementation skeleton: `docs/system/group_query_unification_skeleton.md`
- Current trust level: high
- Current touchpoints:
  - `src/entrypoints/http/group_query_handler.py`
  - `src/notify/usecase.py`
  - `src/adapters/telegram.py`
- Forbidden shortcuts:
  - no duplicate selection engine
  - no `pandas` in final handler
  - no business filtering in HTTP handler

## Phases

1. Selection-path extraction or reuse
2. Formatter split
3. Handler simplification
4. Parity tests

## DoD

- reminder and group query use the same selection semantics
- handler is thin and no longer owns filtering logic
- `pandas` is removed from group query path
