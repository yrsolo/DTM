# Reconstruction Backlog (Concise)

## Purpose
Safe, incremental migration of DTM from legacy tightly coupled automation to maintainable architecture and serverless-ready delivery.

## Current Stage Status
| stage | focus | status | evidence docs |
|---|---|---|---|
| 0 | runtime safety contour, dry-run, baseline, secret gate | done | `doc/02_baseline_validation_and_artifacts.md` |
| 1 | input contracts and data quality stabilization | done | `doc/02_current_modules_and_functionality.md` |
| 2 | layer decomposition (`domain/application/infrastructure`) | done | `doc/10_stage2_layer_inventory.md` |
| 3 | rendering adapter boundary and legacy path cleanup | done | `doc/10_stage2_layer_inventory.md` + Stage 3 task files |
| 4 | reminder fallback/idempotency/parallelism | done | Stage 4 task files in `agile/tasks` |
| 5 | observability, SLI, alert evaluator, runbook cadence | done | `doc/05_risk_register.md`, `doc/02_baseline_validation_and_artifacts.md` |
| 6 | read-model contract and publication path | done | `doc/11`, `doc/12`, `doc/13` |
| 7 | frontend migration prep (schema/fixture/policy/checklists) | done | `doc/14`..`doc/18` |
| 8 | static web prototype and shadow-run evidence package | done | `doc/19`, `doc/20` |
| 9 | serverless deploy contour and cloud runtime wiring | in progress | `doc/21`, `agile/sprint_current.md` |

## Stage 9 Progress
Completed:
- `DTM-76`: main-branch auto-deploy workflow for Yandex Cloud Function.
- `DTM-77`: `.env` to Lockbox sync automation and Google key runtime source.
- `DTM-78`: Lockbox env mapping bound to function, cloud invoke smoke.
- `DTM-80`: agile/process hygiene cleanup and archive normalization.

Completed:
- `DTM-81`: documentation readability refactor (`doc` map + concise backlog shape).

Planned next:
- Cloud-profile shadow-run with explicit `PROTOTYPE_*_S3_KEY` pass criteria.
- Deploy-pipeline consumer contract-regression checks.
- Deployment smoke checklist for Yandex Cloud Function profile.

## Operating Principles
- One active execution task at a time (WIP=1).
- Jira is mandatory lifecycle control plane for each execution task.
- Text docs are hypotheses until freshness/trust check is recorded in `agile/context_registry.md`.
- Historical verbose logs are archived; active docs stay short and readable.

## References
- Documentation map: `doc/00_documentation_map.md`
- Current sprint board: `agile/sprint_current.md`
- Historical full backlog snapshot: `doc/archive/03_reconstruction_backlog_2026-02-27.pre_readability.md`
