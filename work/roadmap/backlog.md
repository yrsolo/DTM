# Backlog

## In Progress
- none

## Blocked
- CAM-2026-03-15-TASK-ATTACHMENTS-LIVE-SMOKE-V1

## Planned
- none

## Done
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
- Separate follow-ups remain outside this campaign:
  - `/info` build metadata 404 in `yc_function_info.py`
  - notify enqueue path inconsistency on test
