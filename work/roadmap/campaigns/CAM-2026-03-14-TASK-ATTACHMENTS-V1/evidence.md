# Evidence - CAM-2026-03-14-TASK-ATTACHMENTS-V1

## Trust gate
- source: active attachment code, current docs, attachment tests, owner-provided campaign proposal
- last_verified_at: 2026-03-14
- verified_by: Codex
- evidence:
  - `src/entrypoints/http/admin_queue_handler.py`
  - `src/jobs/attach_task_file_job.py`
  - `src/snapshot_engine/model.py`
  - `src/snapshot_engine/serialization.py`
  - `src/snapshot_engine/engine.py`
  - `src/snapshot_engine/frontend_v2_payload_builder.py`
  - `src/entrypoints/http/access_context.py`
  - `src/entrypoints/http/router.py`
  - `tests/api/test_command_queue_foundation.py`
  - `tests/jobs/test_attach_task_file_job.py`
  - `tests/snapshot_engine/test_engine_attach_metadata.py`
  - `tests/snapshot_engine/test_query_engine.py`
  - `docs/system/file_attachments.md`
  - `agent/intructions/intruct.md`
- trust_level: high
- notes:
  - current runtime has a pragmatic upload contract plus queued metadata attach, but no finalize, delete, or browser-safe read routes
  - current docs were recently updated and match the narrow existing implementation
  - owner intent is to invest in future-ready architecture before attachments become a live product surface

## Baseline findings
- current attachment metadata lives inside bulk extra snapshot under `TaskExtra.attachments`
- current `AttachmentMeta` is too small for future-ready lifecycle/status/read policy
- current admin routes are:
  - `POST /admin/attachments/request-upload`
  - `POST /admin/commands/attach-task-file`
- current payload publishes attachments directly from prep snapshot and currently does not hide them in masked mode
- current system has no:
  - finalize verification
  - delete lifecycle
  - browser-safe `view/download`
  - canonical attachment service module

## Implementation evidence
- canonical attachment services package added under `src/services/attachments/`
- canonical admin routes added:
  - `POST /ops/admin/task-attachments/request-upload`
  - `POST /ops/admin/task-attachments/finalize`
  - `POST /ops/admin/task-attachments/delete`
- safe read routes added:
  - `GET /ops/api/task-attachments/{attachment_id}/view`
  - `GET /ops/api/task-attachments/{attachment_id}/download`
- legacy routes remain as transitional wrappers only
- attachment metadata model expanded from minimal upload metadata to canonical lifecycle record with future enrichment stub fields
- finalize verifies object existence/size/mime before attach publication
- delete path revokes readability and rebuilds prep
- payload publication now includes only `ready` + visible attachments, with masked mode hiding attachments entirely
- snapshot package exports were changed to lazy loading to avoid an import cycle introduced by the new attachment bounded context

## Verification
- `python -m unittest tests.api.test_command_queue_foundation tests.jobs.test_delete_task_attachment_job tests.jobs.test_attach_task_file_job tests.snapshot_engine.test_engine_attach_metadata tests.snapshot_engine.test_query_engine tests.api.test_frontend_api_routing tests.api.test_task_attachment_read_handler`
- `python scripts/check_no_legacy_entrypoint_imports.py`
- `python scripts/check_no_monsters.py`

## Follow-up evidence: post-mutation cache invalidation
- verified_at: 2026-03-15
- files:
  - `src/entrypoints/http/frontend_response_cache.py`
  - `src/snapshot_engine/stores/s3_store.py`
  - `src/jobs/attach_task_file_job.py`
  - `src/jobs/delete_task_attachment_job.py`
  - `tests/entrypoints/http/test_frontend_response_cache.py`
  - `tests/snapshot_engine/test_s3_store.py`
  - `tests/jobs/test_attach_task_file_job.py`
  - `tests/jobs/test_delete_task_attachment_job.py`
- behavior:
  - successful attach/delete mutations keep prep rebuild inside `SnapshotEngine`
  - after mutation, runtime best-effort invalidates exact default frontend response cache keys for `api|bff` x `masked|full`
  - invalidation failure does not fail the mutation job and is returned as warning
- verification:
  - `python -m unittest tests.entrypoints.http.test_frontend_response_cache tests.snapshot_engine.test_s3_store tests.jobs.test_attach_task_file_job tests.jobs.test_delete_task_attachment_job tests.api.test_frontend_api_routing`

## Follow-up evidence: upload-contract diagnostics
- verified_at: 2026-03-15
- files:
  - `src/entrypoints/http/admin_task_attachments_handler.py`
  - `src/services/attachments/storage.py`
  - `tests/api/test_command_queue_foundation.py`
  - `docs/system/file_attachments.md`
- behavior:
  - `request-upload` still returns the same canonical upload contract fields
  - response now also includes additive `diagnostics` with signed method, signed content type, required headers, upload URL scheme/host/path, UTC expiry timestamp, and a browser preflight note
  - diagnostics are intended to help distinguish frontend misuse from storage/nginx ingress instability without changing finalize or queue semantics
- verification:
  - `python -m unittest tests.api.test_command_queue_foundation`

## Follow-up evidence: structured request-upload errors
- verified_at: 2026-03-15
- files:
  - `src/entrypoints/http/admin_task_attachments_handler.py`
  - `tests/api/test_command_queue_foundation.py`
  - `docs/system/file_attachments.md`
- behavior:
  - `request-upload` keeps the standard JSON error envelope
  - `400/404/503` responses on upload-contract intake now include structured `error.details` with `artifact`, `step`, `reason`, echoed inputs, and missing-field marker when applicable
  - frontend can now distinguish validation rejection from task lookup failure without relying on HTTP status alone
- verification:
  - `python -m unittest tests.api.test_command_queue_foundation`
