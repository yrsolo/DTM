# CAM-2026-03-16-DOC-PREVIEW-CONVERTER-V1 Plan

## Phases

### P01 - Design + Wiring
- `CAM-2026-03-16-DOC-PREVIEW-CONVERTER-V1-P01-T001` Define converter integration and preview lifecycle.
- `CAM-2026-03-16-DOC-PREVIEW-CONVERTER-V1-P01-T002` Add command type + job wiring for preview generation.

### P02 - Runtime Behavior
- `CAM-2026-03-16-DOC-PREVIEW-CONVERTER-V1-P02-T001` Enqueue preview job after `.doc` attach and persist preview state.
- `CAM-2026-03-16-DOC-PREVIEW-CONVERTER-V1-P02-T002` Update read-path semantics for `.doc` view/download.
- `CAM-2026-03-16-DOC-PREVIEW-CONVERTER-V1-P02-T003` Ensure delete best-effort removes preview artifact.

### P03 - Surface + Docs
- `CAM-2026-03-16-DOC-PREVIEW-CONVERTER-V1-P03-T001` Update `/info` harness for preview state visibility.
- `CAM-2026-03-16-DOC-PREVIEW-CONVERTER-V1-P03-T002` Update attachments docs for new `.doc` preview contract.

### P04 - Tests
- `CAM-2026-03-16-DOC-PREVIEW-CONVERTER-V1-P04-T001` Add unit tests for preview job and read-path behavior.
