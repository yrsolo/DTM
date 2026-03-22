# Backlog

## Blocked
- CAM-2026-03-15-TASK-ATTACHMENTS-LIVE-SMOKE-V1

## In Progress
- none

## Planned
- none

## Recent Done
- CAM-2026-03-22-CRITIC2-STRUCTURAL-CLOSEOUT-V1 completed after replacing the visible `snapshot` runtime hub with role-true builders, hiding shell objects behind direct top-entry `handle_*` seams, shrinking the primary browser read orchestration, and removing the named render-job public catalog.
- CAM-2026-03-22-DOCS-CANON-REBUILD-V1 completed after rebuilding active docs around five reader-first sections, archiving the old `integrations` contour and recovery-era architecture trees, and rewriting root/docs navigation for the current system.
- CAM-2026-03-22-LOCAL-GOOGLE-CREDENTIALS-ENV-CLEANUP-V1 completed after removing the checked-in Google key fallback and making local/runtime tooling env-first while leaving cloud deploy on the existing Lockbox `GOOGLE_KEY_JSON` secret path.
- CAM-2026-03-22-PYCACHE-SURFACE-CLEANUP-V1 completed after removing all repo-local `__pycache__` directories outside `.venv`.
- CAM-2026-03-22-HISTORICAL-DOCS-SURFACE-CLEANUP-V1 completed after archiving stale architecture history and reducing active doc READMEs to the current canon plus explicit archive pointers.
- CAM-2026-03-22-ACTIVE-DOCS-RUNTIME-DRIFT-FIX-V1 completed after updating active runtime, snapshot, attachment, and future-queue docs to the current browser-read service split, `platform/runtime/timer_pipeline.py`, and the current attachment APIs.
- CAM-2026-03-22-ACCESS-API-INFO-READ-SPLIT-V1 completed after moving `/info` summary/detail orchestration into an application-owned operational info read service while leaving the HTTP adapter and storage test seam thin and stable.
- CAM-2026-03-22-ATTACHMENTS-PUBLIC-SURFACE-V1 completed after replacing the helper-catalog attachments public surface with one canonical attachments API, one public mime-type contract, and queue handlers only.
- CAM-2026-03-22-SNAPSHOT-PUBLIC-SURFACE-ALIGNMENT-V1 completed after aligning the snapshot public facade with the canonical module API names and removing the leftover capability vocabulary.
- CAM-2026-03-22-TELEGRAM-INTERACTION-SURFACE-V1 completed after replacing the helper-catalog telegram interaction public surface with one application-owned interaction seam shared by webhook and group-query reply execution.
- CAM-2026-03-22-RENDERING-EXECUTION-SURFACE-V1 completed after replacing the helper-catalog rendering public surface with one application-owned execution seam shared by the live rendering jobs.
- CAM-2026-03-22-REMINDERS-DELIVERY-SURFACE-V1 completed after replacing the helper-catalog reminder public surface with one application-owned delivery seam shared by runtime and queue execution.
- CAM-2026-03-22-SNAPSHOT-RUNTIME-HUB-REDUCTION-V1 completed after reducing `snapshot` runtime gravity to smaller builders and direct API dependencies.
- CAM-2026-03-22-BOOTSTRAP-SHELL-EXTRACTION-V1 completed after extracting top-entry shell/webhook/trigger seams out of `bootstrap` into `src/platform/shell`.
- CAM-2026-03-21-ACCESS-API-PRIMARY-READ-SPLIT-V1 completed after moving the primary browser read orchestration into an application-owned service while keeping the thin HTTP adapter and compatibility seams stable.
- CAM-2026-03-21-CRITIQUE-CLOSEOUT-V1 completed after integrating the owner critique into active code and docs instead of leaving it as a free-floating note.
- CAM-2026-03-21-REPO-SURFACE-FINALIZATION-V1 completed after closing the remaining repo-surface cleanup tasks: owner-input shelf naming, last umbrella API test moves, fixture rehome, Russian root README, and active `work/` tracking cleanup.
- CAM-2026-03-21-DATABASE-CONTOUR-REMOVAL-V1 completed after removing the disconnected retired-database contour from the active repo surface.
- CAM-2026-03-21-TESTS-ROOT-REALIGNMENT-V1 completed after rehoming the last umbrella test files.
- CAM-2026-03-21-SRC-TOPLEVEL-CLEANUP-V1 completed after collapsing the active `src` map to the current five-root contour.
- CAM-2026-03-21-SNAPSHOT-MODULE-SURFACE-V1 completed after pushing `snapshot` onto direct runtime/module APIs.
- CAM-2026-03-21-ACCESS-API-PRIMARY-READ-OWNER-V1 completed after making `access_api` the owner of the primary browser read path.

## Parked
- CAM-2026-03-09-RUNTIME-DEPLANNERIZE-V1 (obsolete / already substantially delivered)

## Notes
- Completed campaign records live in `archive/work/campaigns/`.
- New waves should start only from a fresh smell review against the current repo surface.
- `docs/architecture/README.md` is the canonical architecture starting point.
- The only active blocked campaign is live verification that depends on the manual production release workflow, not on additional repo-side refactor work.
