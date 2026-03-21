# CAM-2026-03-21-AGENT-HYGIENE-POLISH-V1

## Goal

Do one focused hygiene pass over `agent/` and nearby helper scripts so they stop advertising removed runtime paths and read as an intentional operator-support contour instead of a pile of stale harnesses.

## Scope

- `agent/**`
- helper scripts/docs that still mention removed `src.legacy`, `src.adapters`, `src.services`, or old archive paths
- light tracking/doc updates for the resulting contour

## Non-goals

- no new runtime architecture redesign
- no attempt to revive or modernize every historical smoke harness
- no changes to owner input files under `agent/intructions/`

## Tasks

- [x] register trust gate from current `agent/` tree and stale-import scan
- [x] rewire active maintenance scripts to current module paths
- [x] archive stale smokes that still depend on removed legacy/runtime shelves
- [x] fix stale archive references and broken encoding in `agent` docs/prompts where needed
- [x] run targeted smoke/import checks for the cleaned contour

## Done when

- active `agent/` utilities import only current paths
- stale legacy-bound smokes no longer live in the active `agent/` root
- `agent` docs point to the current archive home and read cleanly
