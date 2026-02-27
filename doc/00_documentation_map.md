# Documentation Map

This file explains where to read first and where to go for details.

## Read First (5 minutes)
1. `README.md` - product purpose, runtime commands, and current status.
2. `doc/01_current_project_description.md` - what the system does right now.
3. `doc/03_reconstruction_backlog.md` - concise stage status and next execution queue.
4. `agile/sprint_current.md` - current active task and done/remaining counter.

## Core Docs By Purpose
- Current behavior:
  - `doc/01_current_project_description.md`
  - `doc/02_current_modules_and_functionality.md`
- Plan and architecture:
  - `doc/03_reconstruction_backlog.md`
  - `doc/04_target_architecture.md`
- Risk and process:
  - `doc/05_risk_register.md`
  - `doc/09_git_workflow.md`

## Folder Meaning
- `doc/` (top level): only active strategic docs.
- `doc/ops/`: operational runbooks and deployment setup.
- `doc/governance/`: publication/governance/security records.
- `doc/stages/`: stage packages and handoff documents.
- `doc/archive/`: historical snapshots.

## Stage Packages (`doc/stages`)
- Stage 2: `doc/stages/10_stage2_layer_inventory.md`
- Stage 6: `doc/stages/11_stage6_read_model_contract.md`, `doc/stages/12_stage6_ui_view_spec.md`, `doc/stages/13_stage6_closeout_and_handoff.md`
- Stage 7: `doc/stages/14_stage7_execution_plan.md` ... `doc/stages/18_stage7_closeout_and_stage8_handoff.md`
- Stage 8: `doc/stages/19_stage8_execution_plan.md`, `doc/stages/20_stage8_closeout_and_stage9_handoff.md`
- Stage 9 setup: `doc/ops/stage9_main_autodeploy_setup.md`
- Stage 10: `doc/stages/21_stage9_closeout_and_stage10_handoff.md`, `doc/stages/22_stage10_execution_plan.md`
- Stage 11: `doc/stages/23_stage10_closeout_and_stage11_handoff.md`, `doc/stages/24_stage11_retrospective_execution_plan.md`
- Stage 11 closeout: `doc/stages/30_stage11_closeout_and_stage12_handoff.md`
- Stage 12 quality sweep: `doc/stages/31_stage12_code_quality_execution_plan.md`, `doc/governance/stage12_code_quality_standard.md`
- Stage 12 audit artifact: `doc/governance/stage12_module_audit_matrix.md`
- Stage 10 ops drill: `doc/ops/stage10_function_rollback_drill.md`
- Stage 10 owner quickstart: `doc/ops/stage10_owner_quickstart_checklist.md`

## Historical Archives
- Old detailed backlog snapshot:
  - `doc/archive/03_reconstruction_backlog_2026-02-27.pre_readability.md`
- Agile historical snapshots:
  - `agile/archive/sprint_current_2026-02-27.pre_hygiene.md`
  - `agile/archive/context_registry_2026-02-27.pre_hygiene.md`

## Rule
- `doc/*` stores concise, human-readable source docs.
- Detailed historical logs go to `doc/archive/*` and `agile/archive/*`.
