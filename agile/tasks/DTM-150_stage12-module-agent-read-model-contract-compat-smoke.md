# DTM-150: Stage 12 deep cleanup for module `agent.read_model_contract_compat_smoke`

## Context
- Stage 12 switched to deep per-module execution model.
- Module baseline from audit matrix: `agent.read_model_contract_compat_smoke` (`1` item).

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
- [x] Jira key exists (`DTM-150`).
- [x] Jira status set to `В работе`.
- [x] Module cleanup patch applied.
- [x] Relevant checks passed.
- [x] Jira evidence comment added.
- [x] Jira moved to `Готово`.
- [x] Telegram completion sent.

## Work log
- 2026-02-28: Task generated from Stage 12 module queue and linked to module `agent.read_model_contract_compat_smoke`.
- 2026-02-28: Added deterministic payload builder and explicit smoke constants for build id / expected missing-field error.
- 2026-02-28: Checks: `python -m compileall agent`, `.venv\Scripts\python.exe agent\read_model_contract_compat_smoke.py`.

## Links
- Jira: DTM-150
- Inputs:
  - `doc/governance/stage12_module_audit_matrix.md`
  - `doc/governance/stage12_code_quality_standard.md`
