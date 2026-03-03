# CAM-CORE-CLEANUP-V1

## Status
Activated from priority queue after CAM-ENTRYPOINT-REFORM-V1 core scope completion.

## Goal
Keep `core/` domain-only and move infra-coupled runtime pieces to adapters/services/app layers.

## Current Phase
P02: first extraction wave (compatibility-preserving).

## Important Rule
- No business behavior changes during core boundary cleanup.

## Exit Criteria
- `docs/system/core_boundaries.md` lists domain vs infra-coupled core modules.
- first extraction targets are defined and tracked in `work/now/tasks.md`.
- extraction wave for `core/bootstrap.py` and `core/use_cases.py` is completed with shims.
- no runtime regressions introduced by boundary work.

## Archive
- closeouts stored in `work/archive/campaigns/*/closeout.md`.
