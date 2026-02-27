# Reconstruction Backlog (Concise)

## Purpose
Safe, incremental migration of DTM from legacy tightly coupled automation to maintainable architecture and serverless-ready delivery.

## Current Stage Status
| stage | focus | status | evidence docs |
|---|---|---|---|
| 0 | runtime safety contour, dry-run, baseline, secret gate | done | `doc/ops/baseline_validation_and_artifacts.md` |
| 1 | input contracts and data quality stabilization | done | `doc/02_current_modules_and_functionality.md` |
| 2 | layer decomposition (`domain/application/infrastructure`) | done | `doc/stages/10_stage2_layer_inventory.md` |
| 3 | rendering adapter boundary and legacy path cleanup | done | `doc/stages/10_stage2_layer_inventory.md` + Stage 3 task files |
| 4 | reminder fallback/idempotency/parallelism | done | Stage 4 task files in `agile/tasks` |
| 5 | observability, SLI, alert evaluator, runbook cadence | done | `doc/05_risk_register.md`, `doc/ops/baseline_validation_and_artifacts.md` |
| 6 | read-model contract and publication path | done | `doc/stages/11_stage6_read_model_contract.md`, `doc/stages/12_stage6_ui_view_spec.md`, `doc/stages/13_stage6_closeout_and_handoff.md` |
| 7 | frontend migration prep (schema/fixture/policy/checklists) | done | `doc/stages/14_stage7_execution_plan.md` ... `doc/stages/18_stage7_closeout_and_stage8_handoff.md` |
| 8 | static web prototype and shadow-run evidence package | done | `doc/stages/19_stage8_execution_plan.md`, `doc/stages/20_stage8_closeout_and_stage9_handoff.md` |
| 9 | serverless deploy contour and cloud runtime wiring | done | `doc/ops/stage9_main_autodeploy_setup.md`, `doc/ops/stage9_deployment_smoke_checklist.md`, `agile/sprint_current.md` |
| 10 | operations hardening and evidence normalization | in progress | `doc/stages/21_stage9_closeout_and_stage10_handoff.md`, `doc/stages/22_stage10_execution_plan.md`, `agile/sprint_current.md` |

## Stage 9 Progress
Completed:
- `DTM-76`: main-branch auto-deploy workflow for Yandex Cloud Function.
- `DTM-77`: `.env` to Lockbox sync automation and Google key runtime source.
- `DTM-78`: Lockbox env mapping bound to function, cloud invoke smoke.
- `DTM-80`: agile/process hygiene cleanup and archive normalization.

Completed:
- `DTM-81`: documentation readability refactor (`doc` map + concise backlog shape).

Completed:
- `DTM-82`: doc folder restructuring by purpose (`core/ops/governance/stages/archive`) and active-link cleanup.
- `DTM-83`: main deploy trigger executed, workflow recovered via credential fallback, successful deploy run `22500598734`.

Completed:
- `DTM-84`: serverless startup/runtime hotfix (lazy Telegram init + safe import path + HTTP body parsing for invoke payload); deploy run `22501249449`; endpoint healthcheck `!HEALTHY!`.
- `DTM-85`: deployment smoke checklist for Yandex Cloud Function profile (`healthcheck`, `timer dry-run`, `timer live`) with failure triage map.
- `DTM-86`: cloud shadow-run gate with explicit required `PROTOTYPE_*_S3_KEY` pass/fail behavior.
- `DTM-87`: deploy pipeline contract-regression smoke checks before function deployment.

Stage 10 kickoff:
- `DTM-88`: Stage 9 closeout package published and Stage 10 baseline initialized.
- `DTM-89`: rollback drill and recovery notes published for function profile incidents.
- `DTM-90`: deploy run evidence normalization report script and smoke coverage added.
- `DTM-91`: owner quickstart checklist published for daily and weekly serverless operations.

Planned next:
- Stage 10 cloud shadow-run evidence run in required-keys mode with stored artifact.
- Stage 10 closeout and Stage 11 handoff package.

Blocked now:
- `DTM-92`: cloud shadow-run required-mode run failed (`missing_required_cloud_keys`); waiting runtime contour keys.

## Operating Principles
- One active execution task at a time (WIP=1).
- Jira is mandatory lifecycle control plane for each execution task.
- Text docs are hypotheses until freshness/trust check is recorded in `agile/context_registry.md`.
- Historical verbose logs are archived; active docs stay short and readable.

## References
- Documentation map: `doc/00_documentation_map.md`
- Current sprint board: `agile/sprint_current.md`
- Historical full backlog snapshot: `doc/archive/03_reconstruction_backlog_2026-02-27.pre_readability.md`
