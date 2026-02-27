# Context Registry

Purpose: track freshness and trust of planning sources before execution tasking.

## Trust Scale
- `high`: verified against runnable flow/code recently, safe for execution tasking.
- `medium`: partially verified, safe for planning with explicit assumptions.
- `low`: unverified/conflicting; execution blocked until verification task is done.

## Active Registry
| source | last_verified_at | verified_by | evidence | trust_level | notes |
|---|---|---|---|---|---|
| `agile/sprint_current.md` | 2026-02-27 | TeamLead | verified and normalized board to operational format with WIP=1 and explicit Stage 9 counters; active task switched to DTM-82 | high | current sprint control plane in repo |
| `agile/context_registry.md` | 2026-02-27 | TeamLead | trust entries refreshed after doc-structure refactor and active reference checks across README/agile/doc files | high | compact active registry; historical evidence moved to archive |
| `doc/03_reconstruction_backlog.md` | 2026-02-27 | TeamLead | rewritten to concise stage status and active queue format; historical verbose snapshot moved to `doc/archive/03_reconstruction_backlog_2026-02-27.pre_readability.md` | high | now suitable as fast planning source |
| `doc/00_documentation_map.md` | 2026-02-27 | TeamLead | updated with explicit folder semantics (`doc/ops`, `doc/governance`, `doc/stages`, `doc/archive`) and read order | high | primary onboarding path for docs readability |
| `doc/ops/stage9_main_autodeploy_setup.md` | 2026-02-27 | TeamLead | aligned with latest cloud/deploy commits and Stage 9 delivery objective | high | primary Stage 9 setup reference |
| `doc/ops/stage9_deployment_smoke_checklist.md` + live endpoint smoke | 2026-02-27 | TeamLead | validated endpoint responses on current deployed version: `--healthcheck => !HEALTHY!`, `--mode timer --dry-run --mock-external => !GOOD!`; checklist grounded on runnable evidence | high | operational smoke baseline is now explicit and reproducible |
| `.github/workflows/deploy_yc_function_main.yml` contract gate | 2026-02-27 | TeamLead | workflow now executes `read_model_contract_compat_smoke` and `schema_snapshot_smoke` before deploy; local evidence confirms both checks pass | high | deploy now has pre-release consumer contract regression barrier |
| Stage 10 kickoff sources (`doc/03_reconstruction_backlog.md`, `agile/sprint_current.md`, `doc/stages/21...`, `doc/stages/22...`) | 2026-02-27 | TeamLead | Stage 9 completion evidence reconciled with current sprint board and Jira lifecycle (`DTM-76..DTM-87` done) before initializing Stage 10 baseline queue | high | safe to start Stage 10 execution slices without context drift |
| Deploy evidence normalization source (`agent/deploy_run_evidence_report.py` + smoke) | 2026-02-27 | TeamLead | script uses GitHub Actions REST endpoints (`workflow runs` + `run jobs`) and emits stable JSON report; smoke confirms artifact shape and minimum sections | high | deploy evidence can be tracked outside chat/UI screenshots |
| Stage 10 cloud shadow-run runtime contour (`PROTOTYPE_*_S3_KEY`) | 2026-02-27 | TeamLead | uploaded prototype artifacts to Object Storage and reran `agent/stage8_shadow_run_evidence.py --require-cloud-keys`; run passed with evidence artifact `artifacts/shadow_run_stage8/20260227T215711Z_stage8_shadow_run/shadow_run_evidence.json` | high | blocker resolved, cloud required-mode gate is operational |
| Stage 11 retrospective kickoff sources (`doc/stages/23...`, `doc/stages/24...`, `agile/retro.md`) | 2026-02-27 | TeamLead | Stage 10 closeout evidence reconciled with sprint/backlog; Stage 11 reframed to detailed retrospective with explicit slices and corrective-backlog outcome | high | safe to execute deep retrospective without scope ambiguity |
| Stage 11 analytical sources (`doc/stages/25...`, `doc/stages/26...`) | 2026-02-27 | TeamLead | timeline and root-cause clusters documented from completed stage artifacts and Jira lifecycle history | high | prepared input for cost quantification and corrective backlog slicing |
| Stage 11 completion package (`doc/stages/27...` to `doc/stages/30...`) | 2026-02-27 | TeamLead | cost estimate, corrective backlog, review package, and closeout/handoff published with Jira lifecycle closure (`DTM-96..DTM-99`) | high | Stage 11 retrospective is complete and Stage 12 can start from approved corrective priorities |
| Stage 12 pivot sources (owner directive + `doc/stages/31...` + `doc/governance/stage12_code_quality_standard.md`) | 2026-02-27 | TeamLead | owner explicitly redirected Stage 12 from feature/corrective implementation to full code quality sweep; execution plan and quality standard published | high | scope is clear: no feature work, only code quality and readability hardening |
| Stage 12 inventory sources (`agent/build_stage12_audit_matrix.py` + `doc/governance/stage12_module_audit_matrix.md` + `git log`) | 2026-02-27 | TeamLead | generated repo-wide module/class/method matrix (`53` modules, `398` items) and validated recent drift via `git log -n 5`; script hardened for BOM/syntax guard | high | safe baseline for per-module cleanup slices without blind spots |
| Stage 12 core cleanup sources (`core/bootstrap.py`, `core/planner.py`, `core/use_cases.py`, `core/contracts.py`) | 2026-02-27 | TeamLead | first cleanup patch applied (typing/docstrings/readability); `python -m compileall core` passed; timer dry-run failed on external spreadsheet lookup mismatch, not code import/syntax | medium | execution can continue with mock/sanity checks while external sheet contour is stabilized |
| `core/reminder.py` + `utils/service.py` + `index.py` serverless runtime path | 2026-02-27 | TeamLead | reproduced cloud `InvalidToken` import crash and follow-up runtime crash for HTTP invoke payload; fixed eager notifier side effects + added HTTP body parsing in handler; deploy run `22501249449` and endpoint healthcheck confirms `!HEALTHY!` | high | DTM-84 execution evidence complete for runtime/import stability |
| `agent/OPERATING_CONTRACT.md` + `AGENTS.md` + `agent/teamlead.md` | 2026-02-27 | TeamLead | runtime gate re-read this session (`CONTRACT CHECK: OK`) and Jira lifecycle enforced for DTM-84 | high | process source of truth |

## Archive
- Historical detailed evidence log preserved at `agile/archive/context_registry_2026-02-27.pre_hygiene.md`.
- Historical sprint-board log preserved at `agile/archive/sprint_current_2026-02-27.pre_hygiene.md`.
