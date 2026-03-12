# Evidence — CAM-2026-03-12-RUNTIME-DEPLANNERIZE-AND-BOOTSTRAP-HARDENING-V1

## Trust gate
- architecture values: verified
- code evidence: required
- trust level before execution: medium

## Baseline findings to verify
- `index.py` imports bootstrap path into active runtime.
- `planner_runtime_entry.py` creates global context or otherwise causes import-time env coupling.
- tests fail early due to env-dependent imports.

## Required evidence during execution
- code pointers for removed module-level bootstrap
- before/after import smoke outputs
- before/after targeted pytest collection behavior
- list of active call paths no longer planner-centric

## Risks
- hidden compat imports may still pull old config/constants
- bootstrap cleanup may reveal more env coupling elsewhere
