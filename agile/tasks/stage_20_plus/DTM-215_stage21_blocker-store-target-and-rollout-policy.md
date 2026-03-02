# DTM-215: Blocker - store target and rollout policy for next migration stages

## Context
- M1-M5 baseline and scaffolding are in place.
- Next stages (M6+) require concrete rollout policy and store target.

## Blocker
- Need owner decision on:
  1. Operational store target for near-term implementation:
     - continue JSON store as interim primary, or
     - start direct YDB adapter now.
  2. Migration flag rollout policy:
     - when to enable in test contour,
     - when/how to promote to prod contour.

## Why blocked
- Without this decision, further implementation risks rework in core service wiring and publication path.

## Owner next action
1. Confirm store target (`JSON interim` or `YDB now`).
2. Confirm rollout policy (`test-first date` and `prod enable criteria`).
