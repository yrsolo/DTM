# CAM-PIPELINE-CLEAN-SKELETON-V1

## Status
Activated from priority queue after stabilization of CAM-CONFIG-REFORM-V0 hotfix track.

## Goal
Keep runtime entrypoints thin by moving helper logic from `main.py` into dedicated jobs/services modules.

## Current Phase
P03: source-switch orchestration cleanup (compatibility-preserving).

## Important Rule
- No business behavior changes during pipeline cleanup.

## Exit Criteria
- `main.py` orchestration remains behavior-equivalent and helper logic is extracted.
- extraction targets are tracked in `work/now/tasks.md`.
- smoke checks stay green after each atomic extraction.

## Archive
- closeouts stored in `work/archive/campaigns/*/closeout.md`.
