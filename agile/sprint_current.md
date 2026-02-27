# Sprint Current

## Sprint Goal
Keep delivery steady with low-risk, reversible steps toward reconstruction backlog Stage 0.

## Capacity
1 active task (WIP), 3 tasks queued for this short sprint cycle.

## Now
- [IN_PROGRESS] none

## Done
- [DONE] Initial git workflow policy added.
- [DONE] Governance docs added (`AGENTS.md`, `CONTRIBUTING.md`, `SECURITY.md`).
- [DONE] TSK-004 Sprint workspace normalization (`agile/sprint_current.md` structure, Jira keys sync, WIP discipline).
- [DONE] DTM-2 / TSK-009 Source trust gate (`agile/context_registry.md` + pre-task freshness verification).
- [DONE] DTM-3 / TSK-010 README/runtime alignment verification and trust-level upgrade.
- [DONE] DTM-4 / TSK-005 Env contour formalization (`ENV`, `.env.<ENV>`, optional `STRICT_ENV_GUARD`).
- [DONE] DTM-5 / TSK-006 Pipeline run modes and dry-run (`sync-only`, `reminders-only`, `--dry-run` write guard).

## Blocked
- [BLOCKED] none

## Next 3-5 Tasks (Groomed)
- TSK-007 Create baseline validation checklist and artifact capture flow from backlog 0.4.
- TSK-008 Introduce secret scan pre-commit gate (`detect-secrets` or `gitleaks`) from backlog 0.5.

## Selected Work (Jira/Local)
- TSK-004 - Sprint workspace normalization (status: Done)
- DTM-2 - TSK-009 Source trust and freshness gate (status: Done / `Gotovo`)
- TSK-005 - Env contour formalization
  - Jira: DTM-4 (status: Done / `Gotovo`)
- TSK-006 - Pipeline run modes and dry-run
  - Jira: DTM-5 (status: Done / `Ð“Ð¾Ñ‚Ð¾Ð²Ð¾`)
- TSK-007 - Baseline validation checklist
- TSK-008 - Secret scan gate
- DTM-3 - TSK-010 README/runtime alignment verification (status: Done / `Gotovo`)

## Active Task Files
- agile/tasks/DTM-2_source-trust-gate.md
- agile/tasks/DTM-3_readme-runtime-alignment.md
- agile/tasks/DTM-4_env-contour-formalization.md
- agile/tasks/DTM-5_run-modes-and-dry-run.md

## Risks / Blockers
- [BLOCKED] none

## Notes / Decisions
- Prioritize Stage 0 backlog tasks first (safe contour, validation, safety gates).
- Keep WIP limit = 1 to reduce regression risk.
- Before assigning execution tasks, verify source freshness and trust level in `agile/context_registry.md`.
- Jira synchronization started: issues created/linked for TSK-009 and TSK-010, lifecycle managed in Jira first.
- 2026-02-27: Jira runtime access verified from `.env` (REST `/myself` = 200); DTM-5 lifecycle moved `V rabote` -> `Gotovo` with evidence comments.
- 2026-02-27: DTM-5 implemented and smoke-checked (`local_run.py --help`, `local_run.py --mode sync-only --dry-run`).
