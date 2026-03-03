# CAM-DOC-REFORM Charter

## Problem
- Repository had competing documentation roots (`doc/` and `docs/`) and mixed active/historical artifacts.
- Agile files mixed current control-plane data with deep historical execution logs.

## Goal
- Keep one active documentation entrypoint in `docs/`.
- Move historical/legacy material to archive without loss.
- Switch planning IDs to CAM-P-T system for all new work.

## Non-goals
- No product behavior changes.
- No historical document deletion.

## Exit Criteria
- `docs/README.md` is the single active map.
- Legacy `doc/` tree is archived under `docs/archive/doc_legacy/` and replaced with deprecation stub.
- `agile/` has minimal active files (`README.md`, `backlog.md`, `sprint_current.md`) with CAM IDs.

