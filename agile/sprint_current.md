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
- [DONE] DTM-6 / TSK-007 Baseline validation checklist and artifact capture flow.
- [DONE] DTM-7 / TSK-008 Secret scan pre-commit gate hardening and verification.
- [DONE] DTM-8 / TSK-011 Stage 1 required-column validation in repository.
- [DONE] DTM-9 / TSK-012 Stage 1 timing/null input normalization and parser hardening.
- [DONE] DTM-10 / TSK-013 Stage 1 people contract normalization and lookup hardening.
- [DONE] DTM-11 / TSK-014 Reminder runtime compatibility fix (httpx proxy + unicode logging).

## Blocked
- [BLOCKED] none

## Next 3-5 Tasks (Groomed)
- none (prepare next Stage 1 increment)

## Selected Work (Jira/Local)
- TSK-004 - Sprint workspace normalization (status: Done)
- DTM-2 - TSK-009 Source trust and freshness gate (status: Done / `Gotovo`)
- TSK-005 - Env contour formalization
  - Jira: DTM-4 (status: Done / `Gotovo`)
- TSK-006 - Pipeline run modes and dry-run
  - Jira: DTM-5 (status: Done / `Gotovo`)
- TSK-007 - Baseline validation checklist
  - Jira: DTM-6 (status: Done / `Gotovo`)
- TSK-008 - Secret scan gate
  - Jira: DTM-7 (status: Done / `Gotovo`)
- TSK-011 - Stage 1 required task-column validation
  - Jira: DTM-8 (status: Done / `Gotovo`)
- TSK-012 - Stage 1 timing/null input normalization and parser hardening
  - Jira: DTM-9 (status: Done / `Gotovo`)
- TSK-013 - Stage 1 people contract normalization and lookup hardening
  - Jira: DTM-10 (status: Done / `Gotovo`)
- TSK-014 - Reminder runtime compatibility fix
  - Jira: DTM-11 (status: Done / `Gotovo`)
- DTM-3 - TSK-010 README/runtime alignment verification (status: Done / `Gotovo`)

## Active Task Files
- agile/tasks/DTM-2_source-trust-gate.md
- agile/tasks/DTM-3_readme-runtime-alignment.md
- agile/tasks/DTM-4_env-contour-formalization.md
- agile/tasks/DTM-5_run-modes-and-dry-run.md
- agile/tasks/DTM-6_baseline-validation-checklist.md
- agile/tasks/DTM-7_secret-scan-gate.md
- agile/tasks/DTM-8_required-column-validation.md
- agile/tasks/DTM-9_timing-parser-hardening.md
- agile/tasks/DTM-10_people-contract-hardening.md
- agile/tasks/DTM-11_reminder-runtime-compat.md

## Risks / Blockers
- [BLOCKED] none

## Notes / Decisions
- Prioritize Stage 0 backlog tasks first (safe contour, validation, safety gates).
- Keep WIP limit = 1 to reduce regression risk.
- Before assigning execution tasks, verify source freshness and trust level in `agile/context_registry.md`.
- Jira synchronization started: issues created/linked for TSK-009 and TSK-010, lifecycle managed in Jira first.
- 2026-02-27: Jira runtime access verified from `.env` (REST `/myself` = 200); DTM-5 lifecycle moved `V rabote` -> `Gotovo` with evidence comments.
- 2026-02-27: DTM-5 implemented and smoke-checked (`local_run.py --help`, `local_run.py --mode sync-only --dry-run`).
- 2026-02-27: DTM-6 completed (`agent/capture_baseline.py`, baseline docs, smoke-check, Jira `Gotovo`).
- 2026-02-27: DTM-7 completed (full-repo detect-secrets smoke, docs sync, Jira `Gotovo`).
- 2026-02-27: DTM-8 created and moved to `V rabote` as first incremental Stage 1 execution block.
- 2026-02-27: DTM-8 completed (required-column validation + safe row mapping, smoke-check, Jira `Gotovo`).
- 2026-02-27: DTM-9 completed (timing parser null/type hardening + task text normalization, smoke-check, Jira `Gotovo`).
- 2026-02-27: DTM-10 completed (people field normalization + manager lookup hardening, targeted smoke-check, Jira `Gotovo`).
- 2026-02-27: `local_run.py --mode reminders-only --dry-run` still fails in pre-existing reminder path (`httpx.AsyncClient(proxies=...)` + console unicode encoding); tracked for next increment (DTM-11).
- 2026-02-27: DTM-11 completed (`httpx` proxy compatibility + unicode-safe reminder logging); `local_run.py --mode reminders-only --dry-run` passes.
