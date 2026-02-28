# Stage 13 Source-of-Truth and Data Flow Map

Date: 2026-02-28
Task: `DTM-158`

## Objective
Define explicit source-of-truth ownership and data flow boundaries for runtime, publication, and observability paths.

## Source-of-Truth Matrix
| domain | primary source | secondary source | notes |
|---|---|---|---|
| sprint execution state | `agile/sprint_current.md` + Jira statuses | `agile/tasks/*.md` | sprint file reflects current active key and counters; Jira controls lifecycle truth |
| stage-level delivery status | `doc/03_reconstruction_backlog.md` | stage closeout docs in `doc/stages/*` | backlog is concise dashboard, closeout docs keep detailed outcome |
| trust/freshness | `agile/context_registry.md` | smoke evidence logs/artifacts | task decomposition uses trust gate from registry |
| module quality queue | `doc/stages/32_stage12_deep_module_queue.md` | `doc/governance/stage12_module_jira_map.json` | queue file is human view, json map is machine-friendly state |
| runtime config | `config/constants.py` + environment | `.env` / Lockbox mapping | code path defines precedence and defaults |
| production deploy contour | `.github/workflows/deploy_yc_function_main.yml` | `doc/ops/stage9_main_autodeploy_setup.md` | workflow behavior is execution truth |

## Data Flow (Operational)
1. Trigger enters via local launcher or cloud function handler.
2. Runtime config resolves from env and constants (`config/constants.py`).
3. Core planners/managers build/update domain state and reminders.
4. Read-model / schema / fixture artifacts are generated for consumer flows.
5. Smoke scripts verify contracts and operational readiness.
6. Evidence is reflected in Jira comments and synchronized into agile/doc status artifacts.

## Guardrails
- Keep one active execution task (WIP=1).
- No execution without Jira key in `В работе`.
- Every closed task must include smoke/evidence and context update.
- Documentation updates are part of done-state, not post-factum cleanup.
