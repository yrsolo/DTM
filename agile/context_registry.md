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
| Stage 21 live cloud bind (`certificate-manager` + `dns` + `api-gateway`) | 2026-03-02 | TeamLead | both certs moved to `ISSUED`; test/prod domains attached to gateways; DNS CNAME records present | high | cloud domain contour for api is active |
| Frontend API runtime contract (`index.py`, `core/api_payload.py`, `doc/ops/frontend_api_contract.md`) | 2026-03-02 | TeamLead | local invoke smoke for `GET /api/v1/frontend/doc` and `GET /api/v1/frontend` returned `200` + JSON payload marker | high | frontend can consume live task/deadline payload over HTTP |
| Release/test workflow resiliency (`.github/workflows/release_yc_function_prod.yml`, `.github/workflows/deploy_yc_function_main.yml`) | 2026-03-02 | TeamLead | prod release target resolver now supports input/name/id/default fallback; test deploy supports manual `workflow_dispatch` by ref | high | allows test API deploy from `dev` without waiting for `main` push |
| Runtime trigger gate + release source variable path (`index.py`, deploy/release workflows) | 2026-03-02 | TeamLead | verified planner start is gated by known `TRIGGERS` or explicit request `mode`; verified `SOURCE_SHEET_NAME` is sourced from Lockbox secret mapping (not repo vars preflight) in both workflows | high | prevents accidental redraw on arbitrary API calls and removes brittle release variable dependency |
| API doc UX + gateway path handling (`index.py`) | 2026-03-02 | TeamLead | added HTML docs page for `/api/v1/frontend/doc` and resilient path normalization/suffix match for gateway path variants; JSON doc kept via `?format=json` | high | docs endpoint is human-readable and no longer falls to noop because of path shape |
| Migration blueprint package (`docs/*`) + stage scaffolding (`src/*`) | 2026-03-02 | TeamLead | created explicit target architecture, staged migration plan, atomic tasks, data contracts, engineering standards; added non-invasive M1-M3 code skeletons (core normalize + hash gate + service/handler boundaries) | high | migration scope and module boundaries are now explicit without breaking current runtime |
| M1 normalize test baseline (`tests/fixtures/normalize`, `tests/core/normalize`) | 2026-03-02 | TeamLead | added fixture set and unit tests for stage parser, date inference, and normalize interface; `python -m unittest discover -s tests -p \"test_*.py\" -v` passed (8 tests) | high | migration core contracts now have executable quality baseline |
| M2/M3 activation guards (`config/constants.py`, `.env.example`) + hash-gate smoke (`agent/sync_hash_gate_smoke.py`) | 2026-03-02 | TeamLead | added migration feature flags default-off and independent hash-gate smoke script; smoke confirmed first run executes and second run skips on unchanged payload | high | provides safe switch points and executable validation before runtime wiring |
| M2 parity smoke (`agent/normalize_parity_smoke.py`) | 2026-03-02 | TeamLead | implemented lightweight parity check that compares planned stage dates between legacy-style parse and new normalize path on controlled fixtures | medium | scope intentionally narrow (dates only), useful pre-wire guardrail but not full behavioral parity |
| M2 sync handler wiring (`src/handlers/sync.py`, `tests/handlers/test_sync_handler.py`) | 2026-03-02 | TeamLead | replaced placeholder with working hash-gated handler over `SyncService`; unit test confirms first run executes and second unchanged run skips | high | new handler boundary is runnable while prod entrypoints remain unchanged |

## Archive
- `agile/archive/context_registry_2026-02-27.pre_hygiene.md`
- `agile/archive/context_registry_2026-02-28.stage20_agile_cleanup.md`
