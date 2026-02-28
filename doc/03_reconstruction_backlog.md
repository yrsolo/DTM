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
| 9 | serverless deploy contour and cloud runtime wiring | done | `doc/ops/stage9_main_autodeploy_setup.md`, `doc/ops/stage9_deployment_smoke_checklist.md` |
| 10 | operations hardening and evidence normalization | done | `doc/stages/21_stage9_closeout_and_stage10_handoff.md`, `doc/stages/22_stage10_execution_plan.md`, `doc/stages/23_stage10_closeout_and_stage11_handoff.md` |
| 11 | detailed retrospective and corrective backlog | done | `doc/stages/24_stage11_retrospective_execution_plan.md`, `doc/stages/30_stage11_closeout_and_stage12_handoff.md`, `agile/retro.md` |
| 12 | full code quality sweep (no feature work) | done | `doc/stages/31_stage12_code_quality_execution_plan.md`, `doc/governance/stage12_code_quality_standard.md`, `doc/stages/33_stage12_closeout_and_stage13_handoff.md` |
| 13 | post-sweep operating baseline and guardrails refresh | done | `doc/stages/34_stage13_execution_plan.md`, `doc/stages/38_stage13_closeout_and_stage14_handoff.md` |
| 14 | delivery-control clarity (tracking + notification + stage-transition standard) | done | `doc/stages/39_stage14_execution_plan.md`, `doc/stages/42_stage14_closeout_and_stage15_handoff.md` |
| 15 | cloud render verification hardening (deploy wait-gate + timestamp freshness) | done | `doc/stages/43_stage15_execution_plan.md`, `doc/stages/46_stage15_closeout_and_stage16_handoff.md` |
| 16 | multi-LLM reminder runtime expansion (OpenAI/Google/Yandex) | done | `doc/stages/47_stage16_execution_plan.md`, `doc/stages/50_stage16_closeout_and_stage17_handoff.md` |
| 17 | group-chat bot query for tasks and nearest deadlines | done | `doc/stages/51_stage17_execution_plan.md`, `doc/stages/54_stage17_closeout_and_stage18_handoff.md` |
| 18 | provider reliability guardrails (timeout/retry + enhancer counters) | done | `doc/stages/55_stage18_execution_plan.md`, `doc/stages/58_stage18_closeout_and_stage19_handoff.md` |
| 19 | provider failover policy (`draft_only` vs `provider`) | done | `doc/stages/59_stage19_execution_plan.md`, `doc/stages/62_stage19_closeout_and_stage20_handoff.md` |
| 20 | production-readiness hardening (docs freshness, repo hygiene, release evidence) | done | `doc/stages/63_stage20_execution_plan.md`, `doc/stages/66_stage20_closeout_and_stage21_handoff.md` |

## Current Focus (Post Stage 20)
- Active execution task: none (Stage 20 closed).
- Next planned stage: Stage 21 (provider-level SLI and alert policy hardening).

## Operating Principles
- One active execution task at a time (WIP=1).
- Jira is optional; local tracking in `agile/sprint_current.md` + `agile/tasks/*.md` is valid control plane.
- Text docs are hypotheses until freshness/trust check is recorded in `agile/context_registry.md`.
- Historical verbose logs are archived; active docs stay short and readable.

## References
- Documentation map: `doc/00_documentation_map.md`
- Current sprint board: `agile/sprint_current.md`
- Historical full backlog snapshot: `doc/archive/03_reconstruction_backlog_2026-02-27.pre_readability.md`
