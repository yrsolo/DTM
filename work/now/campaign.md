# CAM-ENTRYPOINT-REFORM-V1

## Status
Activated from priority queue after CAM-PIPELINE-CLEAN-SKELETON-V1 handoff.

## Goal
Make `index.py` and `main.py` thin wrappers by moving parsing/routing/orchestration helpers to `src/entrypoints/*`.

## Current Phase
P01: HTTP entrypoint extraction.

## Important Rule
- Keep business behavior unchanged while extracting helpers.

## Exit Criteria
- `index.py` delegates event parsing/routing helpers to `src/entrypoints/http/*`.
- `main.py` delegates job selection shell to `src/entrypoints/jobs/*`.
- External API/runtime behavior remains feature-equivalent.

## Archive
- closeouts stored in `work/archive/campaigns/*/closeout.md`.
