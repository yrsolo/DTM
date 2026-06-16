# Campaign Status Registry

Single source of truth for current campaign lifecycle state.

## Blocked
- CAM-2026-03-15-TASK-ATTACHMENTS-LIVE-SMOKE-V1

## In Progress
- CAM-2026-06-16-SHOWCASE-HERO-VIDEO-COPY-POLISH-V1

## Planned
- none

## Recent Done
- CAM-2026-06-16-SHOWCASE-COPY-MEDIA-POLISH-V1 completed after polishing the showcase media/copy: notification assistant persona, real site screenshot, clearer scheme captions, live product link, and verified Pages deployment.
- CAM-2026-06-15-SHOWCASE-MEDIA-FIX-RASTER-DIAGRAMS-V1 completed after fixing the showcase video path, replacing SVG diagrams with generated raster technical infographics, removing the hero CTA row, rewriting the annotation, and verifying Pages.
- CAM-2026-06-15-SHOWCASE-SHADOWGEN-REDESIGN-V1 completed after the public DTM showcase was redesigned into a shorter ShadowGen-style light landing with tabbed media, accurate hybrid diagrams, saved prompts, and verified Pages deployment.
- CAM-2026-06-15-SHOWCASE-DEPLOY-TECH-DIAGRAMS-V1 completed after deploying the public showcase and refining architecture visuals into technically accurate hybrid diagrams.
- CAM-2026-06-15-GITHUB-PAGES-SHOWCASE-V1 completed after delivering and verifying a public GitHub Pages project showcase for the backend/frontend system.
- CAM-2026-04-26-REMINDER-MODEL-CONFIG-MAP-V1 completed after replacing the morning-specific model config key with a generic `models.openai_by_mode` map and verifying fallback behavior.
- CAM-2026-04-26-MORNING-NOTIFICATIONS-GPT55-V1 completed after routing reminder model selection through the reminders delivery surface and verifying queued/direct morning reminder paths with focused tests.
- CAM-2026-04-09-OBJECT-STORAGE-PUT-INVESTIGATION-V1 completed after tracing active object-storage writes to the scheduled queue/job-status lifecycle, confirming regular 10-minute `update_snapshot` + render bursts, and showing that recent prod attachment and response-cache writes are negligible compared with `jobs/prod/*`.
- CAM-2026-03-22-JOB-STATUS-RETENTION-CLEANUP-V1 completed after adding a platform-owned `cleanup_job_statuses` command, wiring `morning` as a best-effort orchestration slot for cleanup plus reminders, and documenting terminal-status retention in the active runtime canon.
- CAM-2026-03-22-CRITIC3-CANON-ALIGNMENT-V1 completed after renaming the `access_api` primary browser read surface to one explicit read-model term across code, router wiring, module/public seams, and active docs, so the repo and the docs now tell the same calm story about the main browser path.
- CAM-2026-03-22-CRITIC2-STRUCTURAL-CLOSEOUT-V1 completed after replacing `snapshot/internal/runtime_binding.py` with role-true internal builders, tightening `access_api` browser-read seams, shrinking `PrimaryTaskListReadService` via an observability helper, hiding top-entry shell objects behind direct `handle_*` seams, and removing the leftover named-job public shape from `rendering`.
- CAM-2026-03-22-DOCS-CANON-REBUILD-V1 completed after collapsing active docs to `product / architecture / modules / operations / reference`, archiving the old `integrations` plus recovery-era architecture trees, rewriting the root README in Russian, and stripping active docs of migration-era narrative.
- CAM-2026-03-22-LOCAL-GOOGLE-CREDENTIALS-ENV-CLEANUP-V1 completed after removing the checked-in Google key fallback, switching local/runtime tooling to env-first credential resolution, and deleting the root `key/` shelf while keeping cloud deploy on Lockbox-provided `GOOGLE_KEY_JSON`.
- CAM-2026-03-22-PYCACHE-SURFACE-CLEANUP-V1 completed after removing all repo-local `__pycache__` directories outside `.venv`, including root, `src`, `tests`, `agent`, and `config`.
- CAM-2026-03-22-HISTORICAL-DOCS-SURFACE-CLEANUP-V1 completed after moving stale architecture history into `archive/docs/**`, trimming active README paths to the current canon plus explicit archive pointers, and removing `tests/__pycache__` from the active surface.
- CAM-2026-03-22-ACTIVE-DOCS-RUNTIME-DRIFT-FIX-V1 completed after aligning active runtime, snapshot, attachment, and future-queue docs with the current browser-read, timer-pipeline, and attachment API seams instead of deleted handler-era paths.
- CAM-2026-03-22-ACCESS-API-INFO-READ-SPLIT-V1 completed after splitting the giant `/info` reader into a thin HTTP adapter plus an application-owned operational info read service while keeping the existing `_storage_stats` test seam intact.
- CAM-2026-03-22-ATTACHMENTS-PUBLIC-SURFACE-V1 completed after replacing the helper-catalog `attachments.public` surface with one canonical attachments API, a public mime-type contract, and queue handlers while keeping compatibility patch-points local to the internal jobs.
- CAM-2026-03-22-SNAPSHOT-PUBLIC-SURFACE-ALIGNMENT-V1 completed after aligning `snapshot.public` with the canonical module API names and removing the leftover `*capability` grammar.
- CAM-2026-03-22-TELEGRAM-INTERACTION-SURFACE-V1 completed after replacing the helper-catalog `telegram_interaction.public` surface with one application-owned interaction API shared by webhook and group-query reply flows.
- CAM-2026-03-22-RENDERING-EXECUTION-SURFACE-V1 completed after replacing the helper-catalog `rendering.public` surface with one application-owned execution API shared by the rendering job runners.
- CAM-2026-03-22-REMINDERS-DELIVERY-SURFACE-V1 completed after replacing the helper-catalog `reminders.public` surface with one application-owned delivery API shared by queue execution and planner runtime.
- CAM-2026-03-22-SNAPSHOT-RUNTIME-HUB-REDUCTION-V1 completed after replacing the broad internal snapshot runtime bag with smaller role-true builders for stores, query execution, attachment mutations, and update execution.
- CAM-2026-03-22-BOOTSTRAP-SHELL-EXTRACTION-V1 completed after moving shell/webhook/trigger lazy seams into `src/platform/shell`, leaving `bootstrap` focused on context and dependency assembly.
- CAM-2026-03-21-ACCESS-API-PRIMARY-READ-SPLIT-V1 completed after splitting the giant primary browser read handler into a thin HTTP adapter plus an application-owned orchestration service while preserving the old compatibility seams expected by active tests.
- CAM-2026-03-21-CRITIQUE-CLOSEOUT-V1 completed after integrating the owner critique through a bounded cleanup wave: `access_api` now exposes one explicit primary browser read seam, `reminders` no longer exports `SendRemindersJob` publicly, and the beauty audit now describes the repo as strong-but-not-finished instead of already showcase-perfect.
- CAM-2026-03-21-REPO-SURFACE-FINALIZATION-V1 completed after renaming the owner-input shelf, redistributing the remaining umbrella API tests into role-true homes, moving payload snapshots into `tests/fixtures/`, rewriting the root README in Russian, and shrinking active `work/` tracking to current-state summaries.
- CAM-2026-03-21-DATABASE-CONTOUR-REMOVAL-V1 completed after deleting the disconnected retired-database contour and clearing the last obsolete database-migration wording from active code, docs, config, and workflows.
- CAM-2026-03-21-TESTS-ROOT-REALIGNMENT-V1 completed after rehoming the last `tests/services` files into role-true homes.
- CAM-2026-03-21-SRC-TOPLEVEL-CLEANUP-V1 completed after reducing the active `src` contour to `config / contexts / core / entrypoints / platform`.
- CAM-2026-03-21-SNAPSHOT-MODULE-SURFACE-V1 completed after removing the last engine-centered active path from `snapshot`.
- CAM-2026-03-21-ACCESS-API-PRIMARY-READ-OWNER-V1 completed after making `access_api` the clear owner of the primary browser read surface.
- CAM-2026-03-21-REPO-BEAUTY-AUDIT-V1 completed after publishing the beauty audit and the curation method used for the later cleanup waves.

## Archived
- Completed campaigns live in `archive/work/campaigns/`.
- `agent/owner_inputs/**` is owner-provided reference input only and must not be used as execution tracking.

## Rule
- Keep this file aligned with `work/now/tasks.md` and `work/roadmap/backlog.md`.
- Historical closeout detail belongs in `archive/work/campaigns/`, not in this active registry.
