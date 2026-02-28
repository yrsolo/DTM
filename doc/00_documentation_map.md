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
- Stage 10: `doc/stages/21_stage9_closeout_and_stage10_handoff.md` ... `doc/stages/23_stage10_closeout_and_stage11_handoff.md`
- Stage 11: `doc/stages/24_stage11_retrospective_execution_plan.md` ... `doc/stages/30_stage11_closeout_and_stage12_handoff.md`
- Stage 12 quality sweep: `doc/stages/31_stage12_code_quality_execution_plan.md`, `doc/stages/32_stage12_deep_module_queue.md`, `doc/stages/33_stage12_closeout_and_stage13_handoff.md`
- Stage 13: `doc/stages/34_stage13_execution_plan.md` ... `doc/stages/38_stage13_closeout_and_stage14_handoff.md`
- Stage 14: `doc/stages/39_stage14_execution_plan.md` ... `doc/stages/42_stage14_closeout_and_stage15_handoff.md`
- Stage 15: `doc/stages/43_stage15_execution_plan.md` ... `doc/stages/46_stage15_closeout_and_stage16_handoff.md`
- Stage 16: `doc/stages/47_stage16_execution_plan.md` ... `doc/stages/50_stage16_closeout_and_stage17_handoff.md`
- Stage 17: `doc/stages/51_stage17_execution_plan.md` ... `doc/stages/54_stage17_closeout_and_stage18_handoff.md`
- Stage 18: `doc/stages/55_stage18_execution_plan.md` ... `doc/stages/58_stage18_closeout_and_stage19_handoff.md`
- Stage 19: `doc/stages/59_stage19_execution_plan.md` ... `doc/stages/62_stage19_closeout_and_stage20_handoff.md`
- Stage 20: `doc/stages/63_stage20_execution_plan.md` ... `doc/stages/66_stage20_closeout_and_stage21_handoff.md`
- For current status and latest active stage, use `doc/03_reconstruction_backlog.md`.

## Historical Archives
- Old detailed backlog snapshot:
  - `doc/archive/03_reconstruction_backlog_2026-02-27.pre_readability.md`
- Agile historical snapshots:
  - `agile/archive/sprint_current_2026-02-27.pre_hygiene.md`
  - `agile/archive/context_registry_2026-02-27.pre_hygiene.md`

## Rule
- `doc/*` stores concise, human-readable source docs.
- Detailed historical logs go to `doc/archive/*` and `agile/archive/*`.
