

work/roadmap/campaigns/CAM-2026-03-14-TASK-ATTACHMENTS-V1/campaign.md

# CAM-2026-03-14-TASK-ATTACHMENTS-V1

## Status
Proposed

## Owner
Backend

## Goal
Добавить канонический backend contour для вложений задач, совместимый с текущей архитектурой DTM:

- админ может загружать несколько вложений на одну задачу;
- админ может удалять вложения;
- approved users в full access mode могут просматривать и скачивать вложения через browser-safe backend routes;
- attachment metadata публикуется в canonical read side и попадает в frontend payload;
- binary хранится только в Object Storage;
- metadata model сразу предусматривает расширение под future features:
  - LLM summary,
  - extracted text,
  - derived previews,
  - classification/tags/warnings,
  - image/document analysis metadata.

## Why
Сейчас pragmatic v1 upload contour уже позволяет двигаться в сторону attachments, но он ещё не оформлен как полноценная продуктовая boundary/feature.

Нужна отдельная и устойчивая реализация, которая:
- не тащит бинарники через backend runtime;
- не ломает snapshot-first read architecture;
- не смешивает admin mutation flow и user-facing read flow;
- не протекает storage internals в frontend;
- поддерживает multiple attachments per task;
- сразу закладывает canonical metadata model под следующую волну features.

## Scope
### In scope
- request-upload / finalize / delete attachment flow;
- multiple attachments per task;
- support for `docx` and image attachments in v1;
- canonical internal metadata record for attachments;
- frontend-safe task attachment projection;
- browser-safe read routes for `view` and `download`;
- verify-before-attach handshake;
- delete semantics with read revocation;
- orphan / stale upload cleanup policy;
- metadata extension points for future AI/extraction features;
- tests and evidence.

### Out of scope
- in-browser document editing;
- OCR pipeline;
- thumbnail generation pipeline;
- PDF support;
- version history for attachments;
- attachment comments/annotations;
- full-text search inside attachments;
- LLM summary generation itself.

## Product rules
1. Одна задача поддерживает `0..N` вложений.
2. Каждое вложение принадлежит ровно одной задаче.
3. Каждое вложение имеет стабильный `attachment_id`.
4. Supported attachment kinds in v1:
   - `docx`
   - `image`
5. Supported mime types in v1:
   - `application/vnd.openxmlformats-officedocument.wordprocessingml.document`
   - `image/png`
   - `image/jpeg`
   - `image/webp`
6. Unsupported mime/type must be rejected.
7. Attachment становится user-visible только после успешного finalize + verify + attach mutation + publication в read side.
8. Deleted attachment must become non-readable before or at the same time as it disappears from user-visible payload.
9. Masked contour must not expose attachment content.
10. Preferred masked policy for v1: attachments are hidden entirely from masked payload.
11. Full content access is allowed only for trusted/full/authenticated/approved browser access.
12. Storage internals must never leak into frontend payload.

## Architecture constraints
1. Read side remains snapshot-first / prepared-data-first.
2. Attachment metadata must be published through canonical read model, not through ad-hoc per-request storage lookups.
3. Mutating flows (`attach`, `delete`, `cleanup`) are queue-backed jobs.
4. HTTP entrypoints remain thin.
5. Browser auth and access resolution remain at boundary layer.
6. No raw `storage_key` / bucket / object internals in frontend-safe DTOs.
7. No attachment-specific side read model outside canonical snapshot/prep contour.
8. Binary content is never embedded into snapshot payload.
9. Future AI/extraction metadata must live in canonical attachment metadata, not in frontend-only shape.

## User stories
### US-01 Upload one attachment
Админ открывает карточку задачи, выбирает файл, получает upload contract, загружает бинарник напрямую в Object Storage, завершает finalize flow, после чего attachment появляется в задаче.

### US-02 Upload multiple attachments
Админ загружает несколько файлов в одну задачу. Каждый attachment проходит отдельный lifecycle, но все attachments корректно публикуются в одной задаче.

### US-03 View attachment
Approved user в full mode открывает карточку задачи, видит список вложений, нажимает `Open/View` и получает browser-safe просмотр.

### US-04 Download attachment
Approved user в full mode скачивает attachment через backend-owned route.

### US-05 Delete attachment
Админ удаляет attachment из задачи. После удаления attachment исчезает из user-visible payload и становится недоступным для чтения.

### US-06 Failed upload
Если объект не был реально загружен или не прошёл verify по size/mime, attachment не публикуется и остаётся в failed/non-visible state.

### US-07 Future AI metadata
Система хранит дополнительную metadata-обвязку attachment record, чтобы в следующей волне можно было добавить LLM summary/extraction без слома canonical storage model.

## Canonical lifecycle
### Upload / attach
1. Admin calls `request-upload`.
2. Backend validates access and file policy.
3. Backend creates pending attachment metadata record.
4. Backend returns upload contract (presigned upload).
5. Browser uploads binary directly to Object Storage.
6. Admin/browser calls `finalize`.
7. Backend verifies object exists and matches canonical rules.
8. Backend enqueues attach mutation.
9. Worker finalizes attachment metadata.
10. Read side publish/rebuild makes attachment visible in task payload.

### Delete
1. Admin calls `delete`.
2. Backend validates access and attachment/task relation.
3. Backend enqueues delete mutation.
4. Worker revokes read visibility.
5. Worker deletes physical object immediately or marks it for deferred cleanup.
6. Attachment remains non-readable even if physical cleanup is deferred.

### Read
1. Frontend gets task attachment projection from canonical payload.
2. User clicks `view` or `download`.
3. Backend validates browser access context.
4. Backend returns browser-safe read response:
   - short-lived redirect, or
   - proxied/streamed bytes with safe headers.
5. Direct/untrusted/masked access is denied.

## Canonical data model
### Internal attachment metadata record
Attachment metadata must be stored in canonical internal form with room for future enrichment.

Required core fields:
- `attachment_id`
- `task_id`
- `filename_original`
- `filename_display`
- `mime_type`
- `kind`
- `size_bytes`
- `storage_bucket` (internal only)
- `storage_key` (internal only)
- `storage_etag`
- `storage_version`
- `sha256` (optional in v1, preferred if cheap)
- `status`
- `uploaded_by_user_id`
- `uploaded_at`
- `verified_at`
- `deleted_at`
- `deleted_by_user_id`
- `error_code`
- `error_message`
- `snapshot_visible`
- `preview_capabilities`
- `sort_key`

### Future-ready enrichment block
Internal record must also reserve room for future derived metadata:

- `summary_status`
- `summary_text`
- `summary_model`
- `summary_version`
- `summary_generated_at`
- `extracted_text_status`
- `extracted_text_ref`
- `detected_language`
- `page_count`
- `image_width`
- `image_height`
- `preview_state`
- `derived_preview_ref`
- `classification`
- `tags`
- `warnings`
- `custom_meta`

These fields may remain `null` / empty in v1 but must be supported by canonical storage model.

### Frontend-safe projection
Task payload may expose only safe metadata:

- `id`
- `name`
- `mime`
- `kind`
- `sizeBytes`
- `status`
- `uploadedAt`
- `capabilities`
- `links.view`
- `links.download`
- optional lightweight safe `meta`

Must not expose:
- `storage_bucket`
- `storage_key`
- raw object URL
- internal failure/debug-only details unless explicitly allowed for admin-only/debug APIs

## Status model
Suggested statuses:
- `pending_upload`
- `uploaded_unverified`
- `ready`
- `delete_pending`
- `deleted`
- `failed`

Suggested transitions:
- `pending_upload -> uploaded_unverified`
- `uploaded_unverified -> ready`
- `uploaded_unverified -> failed`
- `ready -> delete_pending`
- `delete_pending -> deleted`
- `delete_pending -> failed` only if cleanup failed but read remains revoked
- `pending_upload -> failed` for stale/invalid upload
- `uploaded_unverified -> failed` for verification failure

Only `ready` attachments should be published in normal task payload.

## Access policy
### Upload/delete
Allowed only in admin/operator contour.

### Metadata visibility
Preferred v1 rule:
- `full` mode: attachment metadata visible
- `masked` mode: attachments hidden entirely

### Content access
Allowed only when all conditions are true:
- trusted ingress
- authenticated
- access mode is `full`
- user status is `approved`
- attachment status is `ready`

Otherwise access is denied.

## API plan
### Admin mutation routes
- `POST /ops/admin/task-attachments/request-upload`
- `POST /test/ops/admin/task-attachments/request-upload`
- `POST /ops/admin/task-attachments/finalize`
- `POST /test/ops/admin/task-attachments/finalize`
- `POST /ops/admin/task-attachments/delete`
- `POST /test/ops/admin/task-attachments/delete`

### Browser read routes
- `GET /ops/api/task-attachments/{attachment_id}/view`
- `GET /test/ops/api/task-attachments/{attachment_id}/view`
- `GET /ops/api/task-attachments/{attachment_id}/download`
- `GET /test/ops/api/task-attachments/{attachment_id}/download`

## Module plan
### Entrypoints
- `src/entrypoints/http/admin_task_attachments_handler.py`
- `src/entrypoints/http/task_attachment_read_handler.py`

### Services
- `src/services/attachments/contracts.py`
- `src/services/attachments/policy.py`
- `src/services/attachments/storage.py`
- `src/services/attachments/finalize.py`
- `src/services/attachments/metadata_store.py`
- `src/services/attachments/read_resolver.py`

### Commands
- `src/commands/attach_task_file.py`
- `src/commands/delete_task_attachment.py`
- `src/commands/cleanup_orphan_attachments.py`

### Jobs
- `src/jobs/attach_task_file_job.py`
- `src/jobs/delete_task_attachment_job.py`
- `src/jobs/cleanup_orphan_attachments_job.py`

### Snapshot integration
- update canonical attachment metadata read path
- update `src/snapshot_engine/engine.py`
- update `src/snapshot_engine/frontend_v2_payload_builder.py`

## Key design decisions
1. Multiple attachments are first-class from day one.
2. Upload remains direct-to-storage, not binary-through-function.
3. Finalize must verify object existence and metadata before attach.
4. Delete revokes readability through metadata/read side, not just through physical delete.
5. Browser read routes are separate from admin mutation routes.
6. Metadata model is future-ready for LLM summary/extraction features.
7. Attachment payload is projection-only; binary content stays outside snapshot payload.

## Non-goals
- no office-like collaborative editing;
- no external office viewer dependency as backend contract;
- no public anonymous links;
- no feature-specific alternative read engine;
- no complex media/document processing in this wave.

## Done when
1. Admin can upload multiple supported attachments to one task.
2. Admin can delete one attachment without affecting others.
3. Approved full user can view/download ready attachments.
4. Masked users do not see attachments.
5. Deleted attachments are no longer readable.
6. Failed/unverified attachments are not published.
7. Task payload includes attachment projection in canonical shape.
8. Internal metadata model includes future-ready enrichment fields.
9. Tests cover upload, finalize verify, multiple attachments, delete, access allow/deny, cleanup basics.
10. Evidence is recorded in campaign closeout.


---

work/roadmap/campaigns/CAM-2026-03-14-TASK-ATTACHMENTS-V1/tasks.md

# CAM-2026-03-14-TASK-ATTACHMENTS-V1 Tasks

## P01 — Contracts and metadata model

### CAM-2026-03-14-TASK-ATTACHMENTS-V1-P01-T001
Зафиксировать attachment domain contract:
- supported kinds
- supported mime types
- status model
- upload/finalize/delete semantics
- metadata visibility rules
- content access rules

Acceptance:
- contract documented in campaign/notes
- no ambiguity around masked/full behavior
- no ambiguity around multiple attachments per task

### CAM-2026-03-14-TASK-ATTACHMENTS-V1-P01-T002
Спроектировать canonical internal attachment metadata record.

Acceptance:
- includes core storage-linked metadata
- includes future-ready enrichment block for summary/extraction/preview
- clearly separates internal-only vs frontend-safe fields

### CAM-2026-03-14-TASK-ATTACHMENTS-V1-P01-T003
Спроектировать frontend-safe task attachment projection.

Acceptance:
- contains only safe fields
- supports `view`/`download` links
- deterministic ordering rule is defined

## P02 — Attachment module and policies

### CAM-2026-03-14-TASK-ATTACHMENTS-V1-P02-T001
Создать `src/services/attachments/contracts.py`.

Acceptance:
- canonical DTOs exist
- internal metadata and frontend projection are separated
- future enrichment fields are represented

### CAM-2026-03-14-TASK-ATTACHMENTS-V1-P02-T002
Создать `src/services/attachments/policy.py`.

Acceptance:
- mime support rules implemented
- kind inference implemented
- publish rules implemented
- access policy functions implemented

### CAM-2026-03-14-TASK-ATTACHMENTS-V1-P02-T003
Создать `src/services/attachments/storage.py`.

Acceptance:
- object key builder implemented
- filename sanitization implemented
- presigned upload contract support implemented
- head/verify/delete helpers implemented

## P03 — Request-upload and finalize verify flow

### CAM-2026-03-14-TASK-ATTACHMENTS-V1-P03-T001
Реализовать admin request-upload handler.

Acceptance:
- validates access
- validates task_id / filename / mime / size
- creates pending metadata record
- returns upload contract with stable `attachment_id`

### CAM-2026-03-14-TASK-ATTACHMENTS-V1-P03-T002
Реализовать finalize service in `src/services/attachments/finalize.py`.

Acceptance:
- verifies object exists
- verifies size match
- canonicalizes/validates mime
- produces verified object info
- rejects invalid uploads with stable error codes

### CAM-2026-03-14-TASK-ATTACHMENTS-V1-P03-T003
Реализовать admin finalize handler.

Acceptance:
- validates attachment/task relation
- uses finalize service
- enqueues attach command only after successful verify

## P04 — Attach mutation and canonical metadata publication

### CAM-2026-03-14-TASK-ATTACHMENTS-V1-P04-T001
Расширить или адаптировать `src/jobs/attach_task_file_job.py`.

Acceptance:
- supports multiple attachments per task
- idempotent on repeated delivery
- finalizes canonical attachment metadata state
- makes attachment eligible for read-side publication

### CAM-2026-03-14-TASK-ATTACHMENTS-V1-P04-T002
Создать/реализовать `src/services/attachments/metadata_store.py`.

Acceptance:
- save/read/update attachment metadata operations exist
- lookup by `attachment_id` exists
- lookup by `task_id` exists
- ready-only projection read is supported

### CAM-2026-03-14-TASK-ATTACHMENTS-V1-P04-T003
Интегрировать canonical attachment metadata в read publication contour.

Acceptance:
- no scattered ad-hoc writes outside canonical contour
- attachments are available to payload builder via one canonical path

## P05 — Delete flow

### CAM-2026-03-14-TASK-ATTACHMENTS-V1-P05-T001
Реализовать admin delete handler.

Acceptance:
- validates access
- validates attachment existence and task relation
- enqueues delete command

### CAM-2026-03-14-TASK-ATTACHMENTS-V1-P05-T002
Создать `src/jobs/delete_task_attachment_job.py`.

Acceptance:
- revokes readability/publication
- transitions metadata to delete terminal path
- is idempotent
- does not corrupt other attachments on the same task

### CAM-2026-03-14-TASK-ATTACHMENTS-V1-P05-T003
Определить и реализовать physical cleanup policy.

Acceptance:
- immediate delete best-effort or deferred cleanup is implemented
- deleted attachment is non-readable regardless of object cleanup timing
- policy is documented

## P06 — Browser-safe read routes

### CAM-2026-03-14-TASK-ATTACHMENTS-V1-P06-T001
Создать `src/services/attachments/read_resolver.py`.

Acceptance:
- resolves `view` and `download`
- reads from canonical metadata
- respects access policy
- returns safe redirect/stream result

### CAM-2026-03-14-TASK-ATTACHMENTS-V1-P06-T002
Реализовать `task_attachment_read_handler.py` with `view` route.

Acceptance:
- allows ready attachment view only for trusted/full/approved access
- denies masked/untrusted/non-ready access
- supports browser-friendly response

### CAM-2026-03-14-TASK-ATTACHMENTS-V1-P06-T003
Реализовать `task_attachment_read_handler.py` with `download` route.

Acceptance:
- same access policy as `view`
- proper attachment headers
- no permanent raw storage URL leakage

## P07 — Snapshot/payload integration

### CAM-2026-03-14-TASK-ATTACHMENTS-V1-P07-T001
Расширить `src/snapshot_engine/engine.py` attachment-aware metadata path.

Acceptance:
- engine can consume canonical attachment metadata
- attachment publication is deterministic

### CAM-2026-03-14-TASK-ATTACHMENTS-V1-P07-T002
Расширить `src/snapshot_engine/frontend_v2_payload_builder.py`.

Acceptance:
- task payload contains `attachments`
- only safe fields are included
- only `ready` attachments are published
- multiple attachments are supported

### CAM-2026-03-14-TASK-ATTACHMENTS-V1-P07-T003
Реализовать masked/full publication rule for attachments.

Acceptance:
- masked payload hides attachments entirely
- full payload includes ready attachments
- behavior is consistent across payload and read routes

## P08 — Orphan cleanup and reliability

### CAM-2026-03-14-TASK-ATTACHMENTS-V1-P08-T001
Создать stale/orphan detection rules.

Acceptance:
- `pending_upload` and `uploaded_unverified` stale records are detectable
- stale cutoff/TTL is documented

### CAM-2026-03-14-TASK-ATTACHMENTS-V1-P08-T002
Создать `cleanup_orphan_attachments_job.py` or equivalent cleanup path.

Acceptance:
- stale uploads can be cleaned
- metadata/object drift can be handled at least partially
- policy is not left undefined

### CAM-2026-03-14-TASK-ATTACHMENTS-V1-P08-T003
Обеспечить idempotency and retry safety.

Acceptance:
- repeated attach does not duplicate published attachments
- repeated delete does not resurrect or corrupt state
- finalize retry behavior is defined

## P09 — Future-ready metadata extension points

### CAM-2026-03-14-TASK-ATTACHMENTS-V1-P09-T001
Добавить future enrichment fields to canonical metadata model.

Acceptance:
- summary/extraction/preview/classification fields exist in internal model
- default/null behavior is defined
- v1 runtime remains unaffected when these fields are empty

### CAM-2026-03-14-TASK-ATTACHMENTS-V1-P09-T002
Определить publication policy for future enrichment fields.

Acceptance:
- internal-only fields remain internal
- frontend projection does not accidentally expose non-productized metadata
- future extension path is documented

### CAM-2026-03-14-TASK-ATTACHMENTS-V1-P09-T003
Зафиксировать migration strategy for future LLM summary feature.

Acceptance:
- next wave can add summary job/pipeline without breaking storage model
- no schema redesign should be required for adding summary state/text refs

## P10 — Tests and evidence

### CAM-2026-03-14-TASK-ATTACHMENTS-V1-P10-T001
Добавить unit tests.

Coverage:
- mime policy
- kind inference
- publish rules
- access rules
- metadata defaults
- finalize verification logic

Acceptance:
- tests cover happy-path and failure-path core policies

### CAM-2026-03-14-TASK-ATTACHMENTS-V1-P10-T002
Добавить integration/smoke tests.

Coverage:
- request-upload -> finalize -> published attachment
- multiple attachments on one task
- delete attachment
- denied masked access
- docx happy-path
- image happy-path
- finalize failure on missing object
- finalize failure on size mismatch

Acceptance:
- critical flows are covered end-to-end at service/API level

### CAM-2026-03-14-TASK-ATTACHMENTS-V1-P10-T003
Подготовить evidence pack and closeout notes.

Acceptance:
- route list recorded
- payload examples recorded
- allow/deny examples recorded
- cleanup policy recorded
- known limitations recorded


---

work/roadmap/campaigns/CAM-2026-03-14-TASK-ATTACHMENTS-V1/notes.md

# CAM-2026-03-14-TASK-ATTACHMENTS-V1 Notes

## Supported mime types in v1
### Documents
- `application/vnd.openxmlformats-officedocument.wordprocessingml.document`

### Images
- `image/png`
- `image/jpeg`
- `image/webp`

## Explicitly unsupported in v1
- `application/msword`
- `application/pdf`
- `image/heic`
- `image/svg+xml`
- archives
- executables
- scripts
- unknown binary types

## Attachment kind mapping
- `application/vnd.openxmlformats-officedocument.wordprocessingml.document` -> `docx`
- `image/png` -> `image`
- `image/jpeg` -> `image`
- `image/webp` -> `image`

## Suggested size policy
Exact limits may be configured in code/config, but policy must exist.

Recommended:
- docx: moderate cap
- image: moderate cap
- reject oversized uploads at request-upload and re-check at finalize

## Suggested object key format
`attachments/{task_id}/{attachment_id}/{sanitized_filename}`

## Suggested filename policies
Two separate sanitization paths should exist:
- storage-safe filename
- content-disposition-safe filename

Do not trust original filename as-is for:
- object key
- headers
- logs

## Suggested internal status model
- `pending_upload`
- `uploaded_unverified`
- `ready`
- `delete_pending`
- `deleted`
- `failed`

## Suggested status semantics
### pending_upload
Metadata record created, upload contract issued, object not yet verified.

### uploaded_unverified
Object may exist, but verify/finalize has not completed successfully.

### ready
Attachment is verified and eligible for read-side publication.

### delete_pending
Delete mutation started; attachment should already be treated as non-readable.

### deleted
Attachment is terminally deleted/non-readable.

### failed
Attachment failed upload/verify/finalize or terminally failed cleanup path.

## Publication rule
Only `ready` attachments appear in normal task payload.

## Preferred ordering
Recommended deterministic sort:
1. `uploaded_at ASC`
2. `attachment_id ASC`

Alternative acceptable:
1. `uploaded_at DESC`
2. `attachment_id ASC`

Pick one and keep it stable.

## Preferred masked policy
Attachments are hidden entirely in masked payload.

Reasoning:
- simpler mental model;
- avoids leakage of sensitive document existence;
- keeps masked contour strict.

## Read route policy
### view
Allowed only for:
- trusted ingress
- authenticated
- `full` access mode
- `approved` user status
- `ready` attachment

### download
Same as `view`.

### denied cases
- masked access
- untrusted direct backend access
- unauthenticated access
- non-approved user
- non-ready attachment
- deleted attachment

## Suggested capabilities by kind
### docx
- `browser_view`
- `download`
- `docx_view`

### image
- `browser_view`
- `download`
- `image_inline`

## Verify-before-attach checklist
Finalize must check:
- object exists
- object is readable by backend
- size matches expected size
- mime is allowed
- mime is canonicalized consistently
- object metadata capture succeeds sufficiently for record creation/update

Optional but preferred:
- capture etag
- capture version id
- capture sha256 if cheap/available

## Delete semantics
Delete should be treated as two-layer operation:
1. revoke publication/readability
2. delete physical object or enqueue cleanup

User-visible contract must not depend on physical cleanup finishing immediately.

## Orphan cleanup notes
Need policy for:
- `pending_upload` records older than TTL
- `uploaded_unverified` records older than TTL
- metadata without object
- object without finalized metadata

Minimum acceptable:
- documented stale cutoff and cleanup ownership

Preferred:
- actual cleanup job

## Future-ready metadata block
Canonical internal attachment record should reserve fields for future features.

Suggested fields:
- `summary_status`
- `summary_text`
- `summary_model`
- `summary_version`
- `summary_generated_at`
- `extracted_text_status`
- `extracted_text_ref`
- `detected_language`
- `page_count`
- `image_width`
- `image_height`
- `preview_state`
- `derived_preview_ref`
- `classification`
- `tags`
- `warnings`
- `custom_meta`

## Future-ready status enums
### summary_status
- `none`
- `queued`
- `processing`
- `ready`
- `failed`

### extracted_text_status
- `none`
- `queued`
- `processing`
- `ready`
- `failed`

### preview_state
- `none`
- `queued`
- `processing`
- `ready`
- `failed`

These are internal-only for v1 unless explicitly productized later.

## Projection safety rule
Future enrichment fields must not automatically leak into frontend payload.
Only explicitly productized safe metadata should be projected.

## Known v1 limitations
- no PDF support
- no OCR
- no full-text extraction pipeline
- no thumbnails
- no versioning
- no public links
- no advanced media processing

## Recommended implementation priority
1. contracts and metadata model
2. upload request/finalize verify
3. attach publication
4. delete flow
5. read routes
6. snapshot/payload integration
7. cleanup
8. tests/evidence



Ниже готовые вставки для work/now/campaign.md и work/now/tasks.md.

work/now/campaign.md

# Current Campaign

## Active campaign
- `CAM-2026-03-14-TASK-ATTACHMENTS-V1`

## Goal
Добавить канонический backend contour для task attachments:
- multiple attachments per task;
- admin upload / finalize / delete;
- browser-safe read routes for approved full users;
- canonical attachment metadata publication in task payload;
- future-ready metadata model for summary/extraction/preview enrichment.

## Why now
Attachments are becoming a real product surface.
Current pragmatic upload contour is sufficient as a base, but needs to be hardened and formalized into:
- explicit attachment boundary,
- verify-before-attach flow,
- delete semantics,
- browser-safe read contour,
- canonical metadata model with future enrichment slots.

## Scope for current wave
In:
- request-upload
- finalize verify
- attach mutation
- delete mutation
- browser-safe `view` / `download`
- multiple attachments per task
- support `docx` and `image/*`
- snapshot/frontend payload publication
- orphan cleanup policy
- future-ready metadata fields

Out:
- PDF
- OCR
- thumbnail pipeline
- LLM summary generation
- attachment versioning
- document editing

## Success criteria
- admin can upload multiple attachments to one task;
- admin can delete one attachment independently;
- approved full users can view/download ready attachments;
- masked users do not see attachments;
- failed/unverified attachments are not published;
- internal metadata model includes future-ready enrichment fields;
- tests and evidence are recorded.

work/now/tasks.md

# Current Tasks

## Active campaign
`CAM-2026-03-14-TASK-ATTACHMENTS-V1`

## Current priorities

### 1. Contracts and metadata model
- [ ] Finalize attachment domain contract
- [ ] Finalize supported mime/kind matrix
- [ ] Finalize status model
- [ ] Finalize masked/full visibility policy
- [ ] Finalize canonical internal metadata shape
- [ ] Finalize future-ready enrichment block for summary/extraction/preview

### 2. Attachment service module
- [ ] Create `src/services/attachments/contracts.py`
- [ ] Create `src/services/attachments/policy.py`
- [ ] Create `src/services/attachments/storage.py`
- [ ] Create `src/services/attachments/finalize.py`
- [ ] Create `src/services/attachments/metadata_store.py`
- [ ] Create `src/services/attachments/read_resolver.py`

### 3. Admin mutation flow
- [ ] Implement `admin_task_attachments_handler.py`
- [ ] Implement `request-upload`
- [ ] Implement `finalize`
- [ ] Implement `delete`
- [ ] Keep entrypoints thin

### 4. Jobs and commands
- [ ] Extend `attach_task_file_job.py`
- [ ] Create `delete_task_attachment_job.py`
- [ ] Create `cleanup_orphan_attachments_job.py`
- [ ] Add/align command contracts
- [ ] Ensure idempotency/retry safety

### 5. Read contour
- [ ] Implement `task_attachment_read_handler.py`
- [ ] Implement `view` route
- [ ] Implement `download` route
- [ ] Ensure trusted/full/approved-only content access
- [ ] Deny masked/untrusted/non-ready access

### 6. Snapshot / payload publication
- [ ] Integrate attachment metadata into canonical read path
- [ ] Update `src/snapshot_engine/engine.py`
- [ ] Update `src/snapshot_engine/frontend_v2_payload_builder.py`
- [ ] Publish deterministic attachment list
- [ ] Publish only frontend-safe fields

### 7. Cleanup and reliability
- [ ] Define stale upload TTL
- [ ] Implement orphan detection
- [ ] Implement cleanup path or explicit deferred cleanup contract
- [ ] Ensure deleted attachments remain non-readable even on cleanup failure

### 8. Tests and evidence
- [ ] Add unit tests for policy/finalize/access/projection
- [ ] Add integration tests for upload/finalize/delete/read
- [ ] Add multi-attachment test
- [ ] Add docx/image happy-path tests
- [ ] Add masked deny tests
- [ ] Prepare evidence pack

## Next checkpoint
Deliver canonical upload/finalize/attach path first, then delete, then read routes, then payload publication, then cleanup hardening.

