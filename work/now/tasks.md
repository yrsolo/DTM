# Active Tasks

- CAM-2026-03-15-TASK-ATTACHMENTS-LIVE-SMOKE-V1: `test` live smoke passed end-to-end; `prod` live smoke remains blocked until the manual production release workflow is executed.
- CAM-2026-03-21-SRC-TOPLEVEL-CLEANUP-V1: current cut is the visual `src/` map; dead historical roots are gone, `entrypoints_adapters` is folded into `access_api`, browser masking left `services/access`, the remaining live `services` pieces were moved into `platform` and `snapshot.adapters`, the thin `src/entrypoint` package is folded into `src/entrypoints/root`, loose Telegram/LLM adapters moved into `platform/integrations`, the operational store utility moved into `platform/infra`, provider packages from the old adapter root are redistributed into `platform`, tracked `src/adapters` is gone, `src/app` is folded into `platform` while pure timezone helpers move into `core`, `src/infra` is redistributed into platform integrations plus attachment internals, `src/observability` is folded into `src/platform/observability`, command contracts plus worker runtime are folded into `src/platform/runtime`, and the active top-level map now reads as `archive / config / contexts / core / entrypoints / platform`; the next blocker is no longer a leftover shelf but whether any further reduction would still improve architectural truth.

## Done

- CAM-2026-03-21-SNAPSHOT-MODULE-SURFACE-V1 completed: `snapshot` no longer reads through an engine-centered active surface; `read/query/update` use the runtime bundle directly, attachment mutation semantics moved into a dedicated reusable service, and `SnapshotEngine` now survives only as an internal utility and compatibility-tested detail.
- CAM-2026-03-21-ATTACHMENTS-MODULE-FIRST-FLOW-V1 completed: `attachments` no longer exposes mutation/publication through public `get_*_job` functions; the active entry is now one module-owned command flow in `application`, while jobs remain internal delivery details.
- CAM-2026-03-21-ACCESS-API-PRIMARY-READ-OWNER-V1 completed: `access_api` no longer exposes the primary browser read side through `get_*_handler` and `browser_routes`; it now reads through one scenario-owned browser-read entry rooted in `application`.
- CAM-2026-03-21-FINAL-AESTHETIC-CLOSEOUT-V1 completed: the thin `build_runtime_app_context` alias boundary is gone, the last active `_build_*` helper seams now use `make_*`, and the beauty audit/tracking now describe the repo as closed out rather than still mid-polish.
- CAM-2026-03-21-SHOWCASE-POLISH-V1 completed: root and top-level docs now point first to the active product story and module-first canon, and the repo has an explicit clean first-hop reading path.
- CAM-2026-03-21-MODULE-POLISH-V1 completed: active module methods now read as handlers/capabilities/requests/jobs instead of generic assembly helpers, and the dead broad `get_snapshot_engine()` alias is gone from the active snapshot surface.
- CAM-2026-03-21-ACTIVE-HISTORY-SEPARATION-V1 completed: active runtime docs now keep history available only as compact opt-in pointers instead of foregrounding predecessor material.
- CAM-2026-03-21-BOOTSTRAP-READABILITY-V1 completed: mutable bootstrap seams were removed from `index.py`, dependent tests now use explicit runtime getters, and bootstrap reads as neutral lazy glue instead of a mini control center.
- CAM-2026-03-21-DOCS-VOICE-UNIFICATION-V1 completed: active docs stopped framing the canon as material for future refactor campaigns and replaced the most visible transitional section names with calm current-system language.
- CAM-2026-03-21-ACTIVE-NAMING-CLEANUP-V1 completed: active module docstrings now describe present ownership, and access-api query-owned paths now use `get_snapshot_query_capability` naming instead of broad snapshot-engine wording.
- CAM-2026-03-21-TOP-PATH-ELEGANCE-V1 completed: `index.py` no longer resolves app context eagerly just to classify Telegram HTTP requests, `handler.py` stayed the single obvious top router, and the nearest top-path docs/checks were aligned.
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
- Future beauty child campaigns, if any, are optional taste curation only and should be opened only when a new concrete smell is identified instead of continuing the old mandatory beauty backlog.
- Modular-monolith umbrella campaign is complete and superseded as the primary canon.
- Current active structural cut is the top-level `src` map: dead historical roots are gone, `entrypoints_adapters` is removed, `services/access` is folded into `access_api`, dead service-era shelves in `services/{notify,render,mappers,sync}` are removed from tracked code, tracked `services` is gone, `app/infra/observability/adapters/commands/worker` are folded into role-true homes, and the next decision is whether any further top-level reduction would improve truth or just flatten already-justified structure.
