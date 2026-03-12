# Evidence - CAM-2026-03-12-DOC-CODE-REALIGN-V1

## Trust gate
- source: owner-provided reference bundle, active system docs, verified runtime code
- last_verified_at: 2026-03-12
- verified_by: Codex
- evidence:
  - `agent/intructions/DTM-test/docs/system/architecture_values.md`
  - `docs/system/architecture.md`
  - `docs/system/module_map.md`
  - active runtime entry code
- trust_level: medium
- notes:
  - baseline doc set still reflects multiple architectural eras
  - imported brief is accepted as editorial direction, not auto-verified fact

## Verified baseline findings
- `docs/system/module_map.md` still treats `planner_runtime_entry.py` as OK/canonical
- active docs do not yet expose a main-doc browser auth contract
- active doc set does not clearly state that `agent/intructions/DTM-test/**` is reference-only
- architecture values are not yet maintained as a canonical normative doc in the main `docs/system/*` tree

## Required evidence during execution
- before/after list of stale claims removed
- code pointers supporting updated claims
- list of reclassified stale docs
- proof that main docs link to canonical architecture values
