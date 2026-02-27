# Sprint Current

## Sprint Goal
Start Stage 3 rendering refactor with a shared cell-contract scaffold and reversible extraction slices.

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
- [DONE] DTM-12 / TSK-015 Stage 1 typed Task/Person row-contract scaffolding.
- [DONE] DTM-13 / TSK-016 Stage 1 schema guardrails for task/people row contracts.
- [DONE] DTM-14 / TSK-017 Stage 1 typed data-quality error taxonomy and reporting.
- [DONE] DTM-16 / TSK-019 Stage 1 row-level validation policy for malformed task/person rows.
- [DONE] DTM-17 / TSK-020 Stage 1 timing parse diagnostics and non-fatal error accounting.
- [DONE] DTM-18 / TSK-021 Stage 1 quality report surfacing in local run artifacts.
- [DONE] DTM-15 / TSK-018 Reminder tests: mock OpenAI and Telegram delivery paths.
- [DONE] DTM-19 / TSK-022 Stage 2 layer boundary inventory and dependency map.
- [DONE] DTM-20 / TSK-023 Stage 2 domain module extraction scaffold.
- [DONE] DTM-21 / TSK-024 Stage 2 application use-case orchestration extraction.
- [DONE] DTM-22 / TSK-025 Stage 2 infrastructure adapter boundary for external services.
- [DONE] DTM-23 / TSK-026 Stage 3 calendar rendering shared cell-contract scaffold
- [DONE] DTM-24 / TSK-027 Stage 3 task-calendar renderer alignment
- [DONE] DTM-25 / TSK-028 Stage 3 sheet renderer adapter extraction
- [DONE] DTM-26 / TSK-029 Stage 3 calendar renderer adapter boundary extraction
- [DONE] DTM-27 / TSK-030 Stage 3 render contract parity for calendar header/date cells
- [DONE] DTM-28 / TSK-031 Stage 3 render adapter test harness (dry-run request assertions)
- [DONE] DTM-29 / TSK-032 Stage 3 close-out: TaskManager renderer adapter unification

## Blocked
- [BLOCKED] none

## Next 3-5 Tasks (Groomed)
- [TODO] Stage 3 close-out grooming (coverage review after TaskManager adapter unification)
- [TODO] Stage 4 kickoff grooming (reminder pipeline fallback/idempotency first slice)

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
- TSK-015 - Stage 1 typed Task/Person row-contract scaffolding
  - Jira: DTM-12 (status: Done / `Gotovo`)
- TSK-016 - Stage 1 schema guardrails for task/people row contracts
  - Jira: DTM-13 (status: Done / `Gotovo`)
- TSK-017 - Stage 1 typed data-quality error taxonomy and reporting
  - Jira: DTM-14 (status: Done / `Gotovo`)
- TSK-018 - Reminder tests: mock OpenAI and Telegram delivery paths
  - Jira: DTM-15 (status: Done / `Gotovo`)
- TSK-019 - Stage 1 row-level validation policy for malformed task/person rows
  - Jira: DTM-16 (status: Done / `Gotovo`)
- TSK-020 - Stage 1 timing parse diagnostics and non-fatal error accounting
  - Jira: DTM-17 (status: Done / `Gotovo`)
- TSK-021 - Stage 1 quality report surfacing in local run artifacts
  - Jira: DTM-18 (status: Done / `Gotovo`)
- TSK-022 - Stage 2 layer boundary inventory and dependency map
  - Jira: DTM-19 (status: Done / `Gotovo`)
- TSK-023 - Stage 2 domain module extraction scaffold
  - Jira: DTM-20 (status: Done / `Gotovo`)
- TSK-024 - Stage 2 application use-case orchestration extraction
  - Jira: DTM-21 (status: Done / `Gotovo`)
- TSK-025 - Stage 2 infrastructure adapter boundary for external services
  - Jira: DTM-22 (status: Done / `Gotovo`)
- TSK-026 - Stage 3 calendar rendering shared cell-contract scaffold
  - Jira: DTM-23 (status: Done / `Gotovo`)
- TSK-027 - Stage 3 task-calendar renderer alignment
  - Jira: DTM-24 (status: Done / `Gotovo`)
- TSK-028 - Stage 3 sheet renderer adapter extraction
  - Jira: DTM-25 (status: Done / `Gotovo`)
- TSK-029 - Stage 3 calendar renderer adapter boundary extraction
  - Jira: DTM-26 (status: Done / `Gotovo`)
- TSK-030 - Stage 3 render contract parity for calendar header/date cells
  - Jira: DTM-27 (status: Done / `Gotovo`)
- TSK-031 - Stage 3 render adapter test harness (dry-run request assertions)
  - Jira: DTM-28 (status: Done / `Gotovo`)
- TSK-032 - Stage 3 close-out: TaskManager renderer adapter unification
  - Jira: DTM-29 (status: Done / `Gotovo`)
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
- agile/tasks/DTM-12_typed-row-contract-scaffolding.md
- agile/tasks/DTM-13_schema-guardrails-row-contracts.md
- agile/tasks/DTM-14_typed-data-quality-error-taxonomy.md
- agile/tasks/DTM-15_reminder-tests-mock-openai-telegram.md
- agile/tasks/DTM-16_row-level-validation-policy.md
- agile/tasks/DTM-17_timing-parse-diagnostics.md
- agile/tasks/DTM-18_quality-report-local-artifacts.md
- agile/tasks/DTM-19_stage2-layer-boundary-inventory.md
- agile/tasks/DTM-20_stage2-domain-scaffold.md
- agile/tasks/DTM-21_stage2-application-usecases.md
- agile/tasks/DTM-22_stage2-infra-adapter-boundary.md
- agile/tasks/DTM-23_stage3-render-cell-contract.md
- agile/tasks/DTM-24_stage3-task-calendar-renderer-alignment.md
- agile/tasks/DTM-25_stage3-sheet-renderer-adapter-extraction.md
- agile/tasks/DTM-26_stage3-calendar-renderer-adapter-boundary.md
- agile/tasks/DTM-27_stage3-render-contract-parity-calendar-cells.md
- agile/tasks/DTM-28_stage3-render-adapter-test-harness.md
- agile/tasks/DTM-29_stage3-taskmanager-renderer-adapter-unification.md

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
- 2026-02-27: DTM-12 completed (typed row-contract scaffold for task/person mapping via `core/contracts.py`; timer/reminder dry-run smoke passed).
- 2026-02-27: DTM-13 completed (contract-driven required-header guardrails for tasks/people, smoke-check, Jira `Gotovo`).
- 2026-02-27: DTM-14 completed (typed data-quality error taxonomy + unified missing-header diagnostics in task/people loaders, smoke-check, Jira `Gotovo`).
- 2026-02-27: DTM-15 created as non-urgent backlog task to mock OpenAI/Telegram side effects in reminder tests.
- 2026-02-27: DTM-16 completed (row-level malformed-row fail-soft policy + `row_issues` diagnostics in task/people loaders, smoke-check, Jira `Gotovo`).
- 2026-02-27: DTM-17 completed (structured timing parse diagnostics + non-fatal row-level accounting, smoke-check, Jira `Gotovo`).
- 2026-02-27: DTM-18 completed (quality report surfaced in local runs and baseline artifacts, smoke-check, Jira `Gotovo`).
- 2026-02-27: DTM-15 moved to `V rabote` for reminder test mocks (OpenAI/Telegram external calls disabled in test mode).
- 2026-02-27: DTM-15 completed (mock external reminder mode via `--mock-external`/`mode=test` default, smoke-check, Jira `Gotovo`).
- 2026-02-27: Stage 2 kickoff created in Jira (`DTM-19..DTM-22`); `DTM-19` moved to `V rabote` as single active execution task.
- 2026-02-27: DTM-19 completed (Stage 2 layer boundary inventory + dependency map in `doc/10_stage2_layer_inventory.md`; Jira `Gotovo`).
- 2026-02-27: DTM-20 moved to `V rabote` for Stage 2 scaffold (`S2-SLICE-01`: planner dependency construction boundary extraction).
- 2026-02-27: DTM-20 completed (bootstrap dependency-construction boundary via `core/bootstrap.py`; smoke-check; Jira `Gotovo`).
- 2026-02-27: DTM-21 moved to `V rabote` for Stage 2 application use-case orchestration extraction.
- 2026-02-27: DTM-21 completed (orchestration extracted to `core/use_cases.py`; smoke-check; Jira `Gotovo`).
- 2026-02-27: DTM-22 moved to `V rabote` for Stage 2 infrastructure adapter boundary extraction.
- 2026-02-27: DTM-22 completed (adapter contracts + injected Telegram/OpenAI integration wiring; smoke-check; Jira `Gotovo`).
- 2026-02-27: Stage 3 kickoff created in Jira (`DTM-23..DTM-25`); `DTM-23` moved to `V rabote` as active execution task.
- 2026-02-27: DTM-23 completed (shared `RenderCell` scaffold + TaskCalendarManager contract adoption, sync dry-run smoke, Jira `Gotovo`).
- 2026-02-27: DTM-24 moved to `V rabote` as next single active Stage 3 execution task.
- 2026-02-27: DTM-24 completed (task-calendar renderer alignment into helper methods over shared `RenderCell`; sync dry-run smoke; Jira `Gotovo`).
- 2026-02-27: DTM-25 moved to `V rabote` as next single active Stage 3 execution task.
- 2026-02-27: DTM-25 completed (sheet renderer adapter boundary extraction + bootstrap DI wiring; sync dry-run smoke; Jira `Gotovo`).
- 2026-02-27: Stage 3.1 follow-up kickoff created in Jira (`DTM-26..DTM-28`); `DTM-26` moved to `V rabote` as active execution task.
- 2026-02-27: DTM-26 completed (CalendarManager adapter boundary + bootstrap DI wiring; sync dry-run smoke; Jira `Gotovo`).
- 2026-02-27: DTM-27 moved to `V rabote` as next single active Stage 3 execution task.
- 2026-02-27: DTM-27 completed (CalendarManager render payload parity helpers over `RenderCell`; sync dry-run smoke; Jira `Gotovo`).
- 2026-02-27: DTM-28 moved to `V rabote` as next single active Stage 3 execution task.
- 2026-02-27: DTM-28 completed (adapter dry-run harness assertions via `agent/render_adapter_smoke.py`; smoke checks; Jira `Gotovo`).
- 2026-02-27: DTM-29 moved to `V rabote` as Stage 3 close-out slice for TaskManager renderer adapter unification.
- 2026-02-27: DTM-29 completed (TaskManager adapter unification + bootstrap DI wiring; adapter smoke + sync dry-run; Jira `Gotovo`).
