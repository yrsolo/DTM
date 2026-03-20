# Active Tasks

- CAM-2026-03-21-TOP-PATH-ELEGANCE-V1: remove the remaining top-path ceremony around `index.py` so the first entrypoint path reads cleanly in 3-4 jumps with explicit kill criteria.
- CAM-2026-03-15-TASK-ATTACHMENTS-LIVE-SMOKE-V1: `test` live smoke passed end-to-end; `prod` live smoke remains blocked until the manual production release workflow is executed.

## Done

- CAM-2026-03-21-REPO-BEAUTY-AUDIT-V1 completed: beauty audit published under the module-first canon, a decision-complete sequential backlog was recorded, and the smell-driven execution method for future curation waves is now documented.
- Pre-audit idealization wave completed: active runtime docs now point only to the module-first canon, stale migration-era wording was removed from active narrative, dead `group_query_handler.py` was deleted, and active capability aliases now use capability-true names.
- CAM-2026-03-20-MODULE-FIRST-RECOVERY-V1 completed: module-first canon replaced the active recovery canon, the trust-gated delta audit drove the remaining cleanup, `src/snapshot_engine/*` moved under `src/contexts/snapshot/internal/engine/*`, `src/jobs/*` was removed, and active tests now live under `tests/contexts/*`.
- CAM-2026-03-20-ARCHITECTURE-RECOVERY-V1 completed: architecture-recovery canon delivered the previous recovery wave, top-level competing roots were removed, and the runtime now reads through `entrypoint -> platform/runtime -> owning context`.

- CAM-2026-03-19-MODULARITY-AUDIT-V1 completed: code-verified audit now scores each context for autonomy and records the next decoupling moves.
- CAM-2026-03-19-TEST-ROLLOUT-UNBLOCK-V1 completed: deploy guardrails now accept the active thin-entrypoint contour, and the current `dev` head was deployed to `test` successfully.
- CAM-2026-03-19-MODULAR-MONOLITH-REFORM-V1 completed: modular-monolith refactor umbrella campaign delivered phase-one modularity and now acts as historical precedent for architecture recovery.
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
- Latest bottleneck follow-up remains historical context only; current live execution focus is the blocked `prod` smoke for the attachment contour.
- Future architecture child campaigns must start from `docs/architecture/module-first-recovery/README.md` and the new umbrella campaign trust gate.
- Future beauty child campaigns must execute through `docs/architecture/module-first-recovery/beauty-wave-method.md` and close one smell at a time.
- Modular-monolith umbrella campaign is complete and superseded as the primary canon.
