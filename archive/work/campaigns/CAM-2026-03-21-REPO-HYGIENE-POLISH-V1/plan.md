# CAM-2026-03-21-REPO-HYGIENE-POLISH-V1

## Goal

Do one repo-wide hygiene pass after the architecture cuts so the checked-in tree, active docs, and utility scripts all match the current runtime map.

## Scope

- remove stale temp/runtime shells that survive only as local `__pycache__` directories
- align active docs and helper scripts with the current `src` layout
- document `agent/` so it reads as an intentional operator/agent utility contour instead of a random dump

## Non-goals

- no new architecture redesign
- no business-behavior changes
- no broad archival move of tracked historical roots like `old/` without a separate decision

## Tasks

- [ ] register trust gate from current repo tree, import graph, and active docs/scripts
- [ ] remove stale local-only shells from `src/`, `tests/`, and repo root where only `__pycache__` survives
- [ ] update active docs and helper scripts that still reference removed roots like `src/entrypoint`, `src/app`, `src/infra`, `src/worker`, `src/commands`, `src/observability`, and `src/services/*`
- [ ] add minimal navigation docs for `agent/` and `agent/intructions/`
- [ ] run targeted smoke/guard checks for the updated helpers and docs references

## Done when

- active docs describe only current runtime paths
- helper scripts import only existing current modules
- stale local-only tracked-looking roots no longer clutter the repo tree
- `agent/` has a clear local map
