# priorities_legacy_cut.md

## Priority order
1. CAM-LEGACY-CUT-API-V1
2. CAM-NOTIFY-MODULE-V1
3. CAM-RENDER-MODULE-V1
4. CAM-HTTP-FALLBACK-REMOVAL-V1
5. CAM-LEGACY-PLANNER-DELETE-V1

## Notes
- CAM-GREP-GATES-V1 runs in parallel as anti-relapse guard and must be enabled before deleting planner world.
- Runtime cutover must keep API contract parity (`status` vs `history`) and snapshot-only source-of-truth.
