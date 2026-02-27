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
| Stage 10 cloud shadow-run runtime contour (`PROTOTYPE_*_S3_KEY`) | 2026-02-27 | TeamLead | required-mode run executed: `agent/stage8_shadow_run_evidence.py --require-cloud-keys` failed with `missing_required_cloud_keys` | low | execution blocked until cloud keys are provided in active runtime contour |
| `core/reminder.py` + `utils/service.py` + `index.py` serverless runtime path | 2026-02-27 | TeamLead | reproduced cloud `InvalidToken` import crash and follow-up runtime crash for HTTP invoke payload; fixed eager notifier side effects + added HTTP body parsing in handler; deploy run `22501249449` and endpoint healthcheck confirms `!HEALTHY!` | high | DTM-84 execution evidence complete for runtime/import stability |
| `agent/OPERATING_CONTRACT.md` + `AGENTS.md` + `agent/teamlead.md` | 2026-02-27 | TeamLead | runtime gate re-read this session (`CONTRACT CHECK: OK`) and Jira lifecycle enforced for DTM-84 | high | process source of truth |

## Archive
- Historical detailed evidence log preserved at `agile/archive/context_registry_2026-02-27.pre_hygiene.md`.
- Historical sprint-board log preserved at `agile/archive/sprint_current_2026-02-27.pre_hygiene.md`.
