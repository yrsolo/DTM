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
| Deploy contour split sources (`.github/workflows/deploy_yc_function_main.yml`, `.github/workflows/release_yc_function_prod.yml`) | 2026-03-02 | TeamLead | verified triggers/required vars and test-vs-prod runtime env mapping in workflow files | high | main->test auto, prod->manual |
| Release prep and secret sync (`agent/prepare_prod_release.py`, `agent/sync_lockbox_from_env.py`) | 2026-03-02 | TeamLead | required-key gate added and checked in local dry-run flow | high | release keys cannot be silently missed |
| API domain tooling (`agent/deploy_api_gateway_domain.py`) | 2026-03-02 | TeamLead | verified mode split, function/gateway resolution, domain+certificate input guards | medium | live cloud bind smoke pending in DTM-199 |
| Stage 21 live cloud bind (`certificate-manager` + `dns` + `api-gateway`) | 2026-03-02 | TeamLead | created certificates, ACME CNAME records, test/prod gateways, domain bind attempt failed with `Certificate ... is not valid for domain ...` while certs are `VALIDATING` | medium | execution paused until cert statuses switch to `ISSUED` |
| Frontend API runtime contract (`index.py`, `core/api_payload.py`, `doc/ops/frontend_api_contract.md`) | 2026-03-02 | TeamLead | local invoke smoke for `GET /api/v1/frontend/doc` and `GET /api/v1/frontend` returned `200` + JSON payload marker | high | frontend can consume live task/deadline payload over HTTP |

## Archive
- `agile/archive/context_registry_2026-02-27.pre_hygiene.md`
- `agile/archive/context_registry_2026-02-28.stage20_agile_cleanup.md`
