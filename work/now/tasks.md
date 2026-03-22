# Active Tasks

- CAM-2026-03-15-TASK-ATTACHMENTS-LIVE-SMOKE-V1: `test` live smoke passed end-to-end; the only remaining blocker is rerunning the same smoke after the manual production release workflow is executed.

## Recent Done

- CAM-2026-03-22-CRITIC2-STRUCTURAL-CLOSEOUT-V1 completed: `snapshot` no longer reads through one broad `runtime_binding` hub, `access_api` browser-read seams and frontend observability are calmer, the top path now injects direct `handle_*` seams instead of shell getters, and `rendering.public` no longer exports named render jobs.
- CAM-2026-03-22-DOCS-CANON-REBUILD-V1 completed: active docs were rebuilt around `product / architecture / modules / operations / reference`, the old `integrations` and recovery-era architecture trees moved to `archive/docs/**`, and root/docs navigation was rewritten for the current system instead of the migration story.
- CAM-2026-03-22-LOCAL-GOOGLE-CREDENTIALS-ENV-CLEANUP-V1 completed: the checked-in Google key fallback disappeared, local/runtime tooling now resolves credentials only from env inputs, and cloud deploy continues to use Lockbox-backed `GOOGLE_KEY_JSON`.
- CAM-2026-03-22-PYCACHE-SURFACE-CLEANUP-V1 completed: all repo-local `__pycache__` directories outside `.venv` were removed, so root, `src`, `tests`, `agent`, and `config` read as source-only surfaces again.
- CAM-2026-03-22-HISTORICAL-DOCS-SURFACE-CLEANUP-V1 completed: stale architecture history moved into `archive/docs/**`, active README paths were reduced to the current canon plus explicit archive pointers, and `tests/__pycache__` disappeared from the active repo surface.
- CAM-2026-03-22-ACTIVE-DOCS-RUNTIME-DRIFT-FIX-V1 completed: active runtime, snapshot, attachment, and future-queue docs now point at the current browser-read service split, `platform/runtime/timer_pipeline.py`, and the current attachment read/mutation seams instead of removed handler-era paths.
- CAM-2026-03-22-ACCESS-API-INFO-READ-SPLIT-V1 completed: `/info` now runs through `OperationalInfoReadService`, while `OperationalInfoReadApi` stays as a thin HTTP adapter with the existing `_storage_stats` patch seam preserved for tests.
- CAM-2026-03-22-ATTACHMENTS-PUBLIC-SURFACE-V1 completed: `attachments.public` now exposes one canonical attachments API, the public mime-type contract, and queue handlers only; active HTTP/read/preview/queue consumers use the same module-owned surface.
- CAM-2026-03-22-SNAPSHOT-PUBLIC-SURFACE-ALIGNMENT-V1 completed: `snapshot.public` now uses the same API names as `snapshot.module`, and the leftover `*capability` facade is gone.
- CAM-2026-03-22-TELEGRAM-INTERACTION-SURFACE-V1 completed: `telegram_interaction.public` now exports one canonical interaction API plus the live webhook entry and queue handlers, and both webhook and group-query reply flows use the same module-owned surface.
- CAM-2026-03-22-RENDERING-EXECUTION-SURFACE-V1 completed: `rendering.public` now exports one canonical execution API plus queue handlers, and rendering job runners consume the same module-owned surface.
- CAM-2026-03-22-REMINDERS-DELIVERY-SURFACE-V1 completed: `reminders.public` now exports one canonical delivery API plus queue handlers, and both planner runtime and queue execution consume the same module-owned reminder surface.
- CAM-2026-03-22-SNAPSHOT-RUNTIME-HUB-REDUCTION-V1 completed: `snapshot` application APIs now depend on direct role-true builders instead of one broad runtime bag, and update execution is resolved through the canonical module surface.
- CAM-2026-03-22-BOOTSTRAP-SHELL-EXTRACTION-V1 completed: top-entry shell/webhook/trigger seams now live in `src/platform/shell`, and `bootstrap` is back to boring context/dependency assembly.
- CAM-2026-03-21-ACCESS-API-PRIMARY-READ-SPLIT-V1 completed: the primary browser read path now runs through `PrimaryTaskListReadService`, while `PrimaryTaskListReadApi` stays as a thin HTTP adapter and active compatibility seams remain intact for tests.
- CAM-2026-03-21-CRITIQUE-CLOSEOUT-V1 completed: `access_api` now exposes one explicit primary browser read entry, `reminders` no longer exports `SendRemindersJob` publicly, and the beauty audit no longer overstates showcase readiness.
- CAM-2026-03-21-REPO-SURFACE-FINALIZATION-V1 completed: `agent/owner_inputs` replaced the old owner-input shelf name, the remaining umbrella API tests were redistributed into role-true homes, payload snapshots moved into `tests/fixtures/access_api/`, the root README is now Russian-first, and active `work/` tracking was compressed to current-state summaries.
- CAM-2026-03-21-DATABASE-CONTOUR-REMOVAL-V1 completed: disconnected retired-database code, config toggles, tests, and migration helpers were removed from the active repo surface.
- CAM-2026-03-21-TESTS-ROOT-REALIGNMENT-V1 completed: remaining live API/service-era tests were redistributed into role-true homes.
- CAM-2026-03-21-TESTS-SURFACE-CURATION-V1 completed: empty historical test roots disappeared and the visible top-level `tests/` map was reduced to live homes.
- CAM-2026-03-21-REPO-HYGIENE-POLISH-V1 completed: repo surface docs/scripts/agent maps were aligned and stale local shells were removed.
- CAM-2026-03-21-SRC-TOPLEVEL-CLEANUP-V1 completed: the active `src` map now reads through `config / contexts / core / entrypoints / platform`.
- CAM-2026-03-21-SNAPSHOT-MODULE-SURFACE-V1 completed: `snapshot` no longer reads through an engine-centered active surface.

## Notes

- `agent/owner_inputs/**` is reference-only input and must not be used as execution tracking.
- Active working plans and evidence live in `work/roadmap/campaigns/<CAMPAIGN>/`; completed campaign records move to `archive/work/campaigns/<CAMPAIGN>/`.
- Historical execution detail belongs in archive; this file should stay short and current-state oriented.
