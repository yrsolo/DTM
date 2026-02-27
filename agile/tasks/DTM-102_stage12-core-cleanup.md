# DTM-102: Stage 12 core cleanup (typing/docstrings/style)

## Context
- Stage 12 matrix (`doc/governance/stage12_module_audit_matrix.md`) is published and used as cleanup baseline.
- First implementation slice targets `core/*` modules.

## Goal
- Improve readability and maintainability of `core/*` without feature changes:
  - type annotations consistency,
  - concise and accurate docstrings,
  - style and naming cleanup,
  - removal of obvious local readability debt.

## Non-goals
- No changes to business behavior.
- No API contract redesign.
- No migrations or deployment contour changes.

## Plan
1. Prioritize `core/*` modules by complexity and debt signals from matrix.
2. Apply focused refactor patches with zero behavior drift.
3. Run relevant smoke checks.
4. Record Jira evidence and close task.

## Checklist (DoD)
- [x] Jira key exists (`DTM-102`) and moved to `В работе`.
- [ ] Core cleanup patches applied and reviewed.
- [ ] Relevant smoke checks passed.
- [ ] Jira evidence comment added.
- [ ] Jira moved to `Готово`.
- [ ] Telegram completion sent.

## Work log
- 2026-02-27: Created Jira `DTM-102` and moved it to `В работе`.
- 2026-02-27: Activated Stage 12 `core/*` cleanup slice in sprint board.
- 2026-02-27: Refactored typing/docstrings/readability in `core/bootstrap.py`, `core/planner.py`, `core/use_cases.py`, `core/contracts.py`.
- 2026-02-27: Validation run:
  - `python -m compileall core` passed.
  - `.venv\Scripts\python.exe local_run.py --mode timer --dry-run --mock-external` failed on external source mismatch (`Spreadsheet ... not found`), not on syntax/runtime import.
  - `.venv\Scripts\python.exe -c "<planner/use_cases sanity checks>"` passed.

## Links
- Jira: DTM-102
- Inputs:
  - `doc/governance/stage12_module_audit_matrix.md`
  - `doc/governance/stage12_code_quality_standard.md`
