# Backlog

## In Progress
- CAM-2026-03-20-ARCHITECTURE-RECOVERY-V1

## Blocked
- CAM-2026-03-15-TASK-ATTACHMENTS-LIVE-SMOKE-V1

## Planned
- none

## Done
- CAM-2026-03-19-MODULARITY-AUDIT-V1 completed: current module autonomy and the remaining coupling hotspots are now documented in the active runtime docs.
- CAM-2026-03-19-TEST-ROLLOUT-UNBLOCK-V1 completed: the test deploy guard was aligned with the modular-monolith entrypoint and the latest `dev` head was rolled into `test`.
- CAM-2026-03-19-MODULAR-MONOLITH-REFORM-V1 completed: modular-monolith refactor umbrella wave delivered phase-one modularity and now serves as historical precedent for the recovery program.
- Docs IA refresh completed: active docs moved into `product/`, `architecture/`, `integrations/`, `operations/`, and `reference/`, with archive folders now indexed by local `README.md`.
- Legacy `.doc` preview converter wave completed: external converter integrated, preview job added, and `.doc` view/download split behavior documented.
- Attachment upload allowlist now includes `.doc` (`application/msword`) and `.pdf` (`application/pdf`) alongside existing `docx` and image formats.
- Recent completed campaigns were archived under `work/archive/campaigns/`.
- Latest archived closeouts include the 2026-03-12 execution wave, 2026-03-14 attachment/people/audit waves, and the completed attachment cleanup wave.

## Parked
- CAM-2026-03-09-RUNTIME-DEPLANNERIZE-V1 (obsolete / already substantially delivered)

## Notes
- Current live execution focus is the blocked `prod` confirmation step for `CAM-2026-03-15-TASK-ATTACHMENTS-LIVE-SMOKE-V1`.
- `agent/intructions/DTM-test/**` is reference-only and not part of execution/archive lifecycle.
- `CAM-2026-03-20-ARCHITECTURE-RECOVERY-V1` is the canonical architecture umbrella campaign; child campaigns should be opened only after trust-gate refresh against the recovery docs and current code.
- Separate follow-ups remain outside this campaign:
  - `/info` build metadata 404 in `yc_function_info.py`
  - notify enqueue path inconsistency on test
