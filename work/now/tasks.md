# Active Tasks

- CAM-2026-03-15-TASK-ATTACHMENTS-LIVE-SMOKE-V1: `test` live smoke passed end-to-end; `prod` live smoke remains blocked until the manual production release workflow is executed.

## Done

- Docs IA refresh completed: `docs/` is now reorganized by reader intent with Russian onboarding READMEs, relative repo links, and archive folder indexes.
- Legacy `.doc` preview converter wave completed: `.doc` view now resolves to PDF preview while download returns original, with async preview job and updated operator harness.
- Info attachment harness now includes step pipeline visualization, per-step JSON panel, and preview-job stage tracking.
- Converter shared token is now wired from Lockbox key `SHARED_TOKEN` into `DOC_PREVIEW_CONVERTER_SHARED_TOKEN`.
- Attachment upload allowlist now includes `.doc` (`application/msword`) and `.pdf` (`application/pdf`) alongside existing `docx` and image formats.
- Recent attachment wave is complete on `test`: upload, finalize, worker attach, publication, view/download, delete, cache invalidation, and `/test/ops/info` verification harness are all live and documented.
- Attachment cleanup wave is complete: stale `pending_upload`, `uploaded_unverified`, and `deleted` metadata is cleaned via hidden `cleanup_task_attachments` command with 24h TTL and single-pass prep rebuild semantics.
- People snapshot and secret-only people API wave is complete, including `contactEmail`, `yandexEmail`, and derived `isActive` behavior.
- 2026-03-12 runtime, metrics, diagnostics, and doc-realignment campaigns are complete and archived as historical execution waves.

## Notes

- `agent/intructions/DTM-test/**` is reference-only input and must not be used as execution tracking.
- Working plans and evidence must live only in `work/roadmap/campaigns/<CAMPAIGN>/`.
- Telegram/reminder/group-query remains frozen for this wave unless break/fix work is required.
- Latest bottleneck follow-up remains historical context only; current live execution focus is the blocked `prod` smoke for the attachment contour.
