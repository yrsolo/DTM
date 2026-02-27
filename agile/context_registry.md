# Context Registry

Purpose: track freshness and trust of planning sources before execution tasking.

## Trust Scale
- `high`: verified against runnable flow/code recently, safe for execution tasking.
- `medium`: partially verified, safe for planning with explicit assumptions.
- `low`: unverified/conflicting; execution blocked until verification task is done.

## Active Registry
| source | last_verified_at | verified_by | evidence | trust_level | notes |
|---|---|---|---|---|---|
| `agile/sprint_current.md` | 2026-02-27 | TeamLead | verified and normalized board to operational format with WIP=1 and explicit Stage 9 counters | high | current sprint control plane in repo |
| `agile/context_registry.md` | 2026-02-27 | TeamLead | trust entries refreshed after `git status --short --branch` and recent history checks on sprint/context/backlog docs | high | compact active registry; historical evidence moved to archive |
| `doc/03_reconstruction_backlog.md` | 2026-02-27 | TeamLead | checked against latest commits (`DTM-76..DTM-78`) and Stage 9 scope continuity | medium | strategic backlog source; execution state tracked in sprint/Jira |
| `doc/21_stage9_main_autodeploy_setup.md` | 2026-02-27 | TeamLead | aligned with latest cloud/deploy commits and Stage 9 delivery objective | high | primary Stage 9 setup reference |
| `agent/OPERATING_CONTRACT.md` + `AGENTS.md` + `agent/teamlead.md` | 2026-02-27 | TeamLead | runtime gate re-read this session (`CONTRACT CHECK: OK`) and Jira lifecycle enforced for DTM-80 | high | process source of truth |

## Archive
- Historical detailed evidence log preserved at `agile/archive/context_registry_2026-02-27.pre_hygiene.md`.
- Historical sprint-board log preserved at `agile/archive/sprint_current_2026-02-27.pre_hygiene.md`.
