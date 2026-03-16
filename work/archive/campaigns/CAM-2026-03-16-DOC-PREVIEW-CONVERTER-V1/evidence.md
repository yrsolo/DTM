# CAM-2026-03-16-DOC-PREVIEW-CONVERTER-V1 Evidence

## Completed Tasks
- [x] `CAM-2026-03-16-DOC-PREVIEW-CONVERTER-V1-P01-T001`
- [x] `CAM-2026-03-16-DOC-PREVIEW-CONVERTER-V1-P01-T002`
- [x] `CAM-2026-03-16-DOC-PREVIEW-CONVERTER-V1-P02-T001`
- [x] `CAM-2026-03-16-DOC-PREVIEW-CONVERTER-V1-P02-T002`
- [x] `CAM-2026-03-16-DOC-PREVIEW-CONVERTER-V1-P02-T003`
- [x] `CAM-2026-03-16-DOC-PREVIEW-CONVERTER-V1-P03-T001`
- [x] `CAM-2026-03-16-DOC-PREVIEW-CONVERTER-V1-P03-T002`
- [x] `CAM-2026-03-16-DOC-PREVIEW-CONVERTER-V1-P04-T001`

## Trust Gate
- source: `src/services/attachments/read_resolver.py`, `src/jobs/attach_task_file_job.py`, `src/services/attachments/storage.py`, `src/services/attachments/metadata_store.py`, `src/commands/types.py`, `src/worker/dispatcher.py`
  - last_verified_at: 2026-03-16
  - verified_by: Codex
  - evidence: direct file inspection in repo
  - trust_level: high
  - notes: current read-path always redirects to original object; no preview lifecycle wiring exists
- source: external converter OpenAPI (`/openapi.json`)
  - last_verified_at: 2026-03-16
  - verified_by: Codex
  - evidence: converter exposes `POST /convert/doc-to-pdf` with `source_url` and `target_url` plus optional `x-shared-token`
  - trust_level: medium
  - notes: contract does not include target headers; plan uses headerless presigned upload

## Verification
- Command:
  - `python -m unittest tests.services.test_attachment_policy tests.api.test_task_attachment_read_handler tests.jobs.test_attach_task_file_job tests.jobs.test_generate_attachment_preview_job tests.jobs.test_delete_task_attachment_job tests.api.test_info_observability`
- Result:
  - `OK`

## Notes
- Secrets must stay in Lockbox; do not store converter URL/token in repo.
