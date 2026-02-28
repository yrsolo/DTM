# Context Registry

Purpose: track freshness and trust of planning sources before execution tasking.

## Trust Scale
- `high`: verified against runnable flow/code recently, safe for execution tasking.
- `medium`: partially verified, safe for planning with explicit assumptions.
- `low`: unverified/conflicting; execution blocked until verification task is done.

## Active Registry
| source | last_verified_at | verified_by | evidence | trust_level | notes |
|---|---|---|---|---|---|
| `agent/OPERATING_CONTRACT.md`, `AGENTS.md`, `agent/teamlead.md` | 2026-02-28 | TeamLead | runtime start gate completed in chat (`CONTRACT CHECK: OK`) | high | process source of truth |
| `agile/sprint_current.md` | 2026-02-28 | TeamLead | compacted board to latest-stage focus; Stage 20 counters and Stage 21 queue aligned | high | active sprint control plane |
| `agile/tasks/**` structure (`DTM-197`) | 2026-02-28 | TeamLead | moved task files from one flat folder into staged subfolders (`stage_00_09`, `stage_10_19`, `stage_20_plus`, `foundation_misc`) and added `agile/tasks/README.md` | high | improves navigation without data loss |
| `agile/strategy.md` | 2026-02-28 | TeamLead | updated objectives and constraints to production-readiness and Stage 21 scope | high | concise strategic baseline |
| `agile/retro.md` | 2026-02-28 | TeamLead | replaced outdated Stage 11-heavy content with Stage 20 retrospective and Stage 21 retro focus | high | current retrospective context |
| `README.md` | 2026-02-28 | TeamLead | reduced duplicated stage-link dump; kept active runbook pointers | high | onboarding remains accurate |
| `doc/00_documentation_map.md` | 2026-02-28 | TeamLead | stage package index refreshed through Stage 20 | high | authoritative doc navigation |
| `doc/03_reconstruction_backlog.md` | 2026-02-28 | TeamLead | compact stage status updated: Stage 20 done, Stage 21 proposed | high | concise backlog source |
| `.github/workflows/deploy_yc_function_main.yml` | 2026-02-28 | TeamLead | still includes contract smoke gate before deploy | high | deploy guard preserved |
| Stage 20 doc hardening package | 2026-02-28 | TeamLead | published `doc/stages/63..66` + `doc/ops/stage20_*` | high | production-readiness evidence complete |
| Stage 20 smoke evidence (`compileall`, provider/failover/group-query/reminder smokes) | 2026-02-28 | TeamLead | all checks passed during Stage 20 execution | high | ready for manual cloud go/no-go checks |
| Cloud runtime baseline (`index.py`, `core/reminder.py`, `utils/service.py`) | 2026-02-27 | TeamLead | prior runtime token/import crash fixed; healthcheck invoke stable | high | serverless startup path stable |

## Archive
- `agile/archive/context_registry_2026-02-27.pre_hygiene.md`
- `agile/archive/context_registry_2026-02-28.stage20_agile_cleanup.md`
