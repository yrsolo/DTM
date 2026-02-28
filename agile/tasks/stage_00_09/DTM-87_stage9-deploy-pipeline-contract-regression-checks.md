# DTM-87: Stage 9 deploy-pipeline contract regression checks

## Context
- Stage 9 deploy pipeline published function versions without a hard contract gate.
- Read-model consumer contract regressions must fail early before deploy.

## Goal
- Add mandatory contract smoke checks to main deploy workflow before cloud deploy step.
- Keep checks lightweight and reproducible in CI runner.

## Non-goals
- No E2E business-flow checks in this task.
- No change to runtime deployment target or trigger logic.

## Plan
1. Add Python setup + dependency install in deploy workflow.
2. Add contract smoke step (`read_model_contract_compat_smoke`, `schema_snapshot_smoke`) before deploy.
3. Update Stage 9 ops docs and README mention.
4. Run local smoke commands to mirror CI gate.

## Checklist (DoD)
- [x] Jira key exists (`DTM-87`) and moved to `В работе`.
- [x] Deploy workflow contains pre-deploy contract smoke step.
- [x] Local run of smoke commands passes.
- [x] Docs updated for new gate.
- [x] Jira evidence comment added.
- [x] Jira moved to `Готово`.
- [x] Telegram completion sent.

## Work log
- 2026-02-27: Created Jira `DTM-87`, moved to `В работе`.
- 2026-02-27: Added contract regression smoke stage to `.github/workflows/deploy_yc_function_main.yml`.
- 2026-02-27: Updated `doc/ops/stage9_main_autodeploy_setup.md` and `README.md`.
- 2026-02-27: Local smoke evidence captured (`read_model_contract_compat_smoke_ok`, `schema_snapshot_smoke_ok`), Jira moved to `Готово`, owner notified.

## Links
- Jira: DTM-87
- Files:
  - `.github/workflows/deploy_yc_function_main.yml`
  - `agent/read_model_contract_compat_smoke.py`
  - `agent/schema_snapshot_smoke.py`
  - `doc/ops/stage9_main_autodeploy_setup.md`
