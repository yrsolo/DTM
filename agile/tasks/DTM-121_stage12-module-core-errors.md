# DTM-121: Stage 12 deep cleanup for module `core.errors`

## Context
- Stage 12 switched to deep per-module execution model.
- Module baseline from audit matrix: `core.errors` (`7` items).

## Goal
- Perform deep quality cleanup for this module without feature behavior changes:
  - typing completeness,
  - accurate concise docstrings,
  - readability and local structure cleanup,
  - removal of obvious dead or misleading fragments.

## Non-goals
- No business logic redesign.
- No interface contract expansion.
- No unrelated cross-module refactor.

## Plan
1. Analyze the module and identify highest-impact readability/type debt.
2. Apply focused refactor patches preserving behavior.
3. Run relevant smoke checks.
4. Record Jira evidence and close the task.

## Checklist (DoD)
- [x] Jira key exists (`DTM-121`).
- [x] Jira status set to `В работе`.
- [ ] Module cleanup patch applied.
- [ ] Relevant checks passed.
- [ ] Jira evidence comment added.
- [ ] Jira moved to `Готово`.
- [ ] Telegram completion sent.

## Work log
- 2026-02-28: Task generated from Stage 12 module queue and linked to module `core.errors`.

## Links
- Jira: DTM-121
- Inputs:
  - `doc/governance/stage12_module_audit_matrix.md`
  - `doc/governance/stage12_code_quality_standard.md`
