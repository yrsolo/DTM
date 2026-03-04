# CAM-DEDUP-LEGACY-REMOVAL-V1

## Status
Activated from priority queue after `main.py` thin-entrypoint extraction wave reached stable state.

## Goal
Remove parallel duplicate implementations in runtime-adjacent roles (sync/readmodel/handlers) and define one source of truth per role.

## Current Phase
P01: duplicate inventory and keep/remove decisions.

## Important Rule
- No business behavior changes during dedup mapping; removal goes in follow-up atomic PRs only.

## Exit Criteria
- `docs/system/dedup_plan.md` contains role-based keep/remove map.
- duplicates selected for removal are not imported by active runtime contour.
- removal PRs are small, reversible, smoke-checked.

## Archive
- closeouts stored in `work/archive/campaigns/*/closeout.md`.
