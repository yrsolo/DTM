# CAM-2026-03-22-ATTACHMENTS-PUBLIC-SURFACE-V1 Plan

## Trust Gate
- source: `src/contexts/attachments/public.py`, `src/entrypoints/http/admin_task_attachments_handler.py`, `src/contexts/access_api/internal/task_attachment_read_api.py`, `src/contexts/attachments/internal/job_runners.py`
- last_verified_at: 2026-03-22
- verified_by: Codex
- evidence:
  - `rg -n "from src\\.contexts\\.attachments\\.public import|import src\\.contexts\\.attachments\\.public|get_public_api\\(|get_attachment_storage\\(|get_attachment_metadata_store\\(|get_attachment_finalize_service\\(|get_attachment_read_resolver\\(|get_doc_preview_converter\\(|get_attachment_snapshot_api\\(|get_attachment_command_flow\\(" src tests`
  - direct reads of active attachments runtime and access paths
- trust_level: high
- notes:
  - `attachments.public` still sat on live HTTP, read-side, preview, and queue flows as a helper catalog over one real module surface.

## Phases

### P01 - Canonical Attachments API
- `CAM-2026-03-22-ATTACHMENTS-PUBLIC-SURFACE-V1-P01-T001` Replace the helper-catalog attachment public surface with one canonical attachments API plus public mime-type contract.
- `CAM-2026-03-22-ATTACHMENTS-PUBLIC-SURFACE-V1-P01-T002` Repoint active HTTP, read, preview, and queue consumers to the canonical attachments API.

### P02 - Verification And Tracking
- `CAM-2026-03-22-ATTACHMENTS-PUBLIC-SURFACE-V1-P02-T001` Run the targeted attachments/access-api/guardrail contour.
- `CAM-2026-03-22-ATTACHMENTS-PUBLIC-SURFACE-V1-P02-T002` Close out local tracking and archive the completed campaign record.
