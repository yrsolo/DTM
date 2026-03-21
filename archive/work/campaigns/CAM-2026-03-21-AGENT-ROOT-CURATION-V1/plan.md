# CAM-2026-03-21-AGENT-ROOT-CURATION-V1

## Goal

Turn the active `agent/` root from a flat pile of unrelated helpers into a readable operator contour where only contract/control files stay at the top and the rest lives in role-true subfolders.

## Scope

- `agent/**`
- live file-path references in workflows, agent helpers, and active docs/tracking

## Non-goals

- no runtime architecture redesign in `src/`
- no rewriting owner input files under `agent/intructions/`
- no revival of archived legacy smokes

## Tasks

- [x] register trust gate from current `agent/` tree and live path references
- [x] group active deploy helpers into a deploy-owned subfolder
- [x] group prototype/web-payload helpers into a prototype-owned subfolder
- [x] group artifact/evidence builders into an artifacts/evidence-owned subfolder
- [x] group operational migration helpers into a migration-owned subfolder
- [x] group reminder-oriented harnesses into a reminder-owned subfolder
- [x] move generic active smokes out of the root into a dedicated smoke shelf
- [x] refresh `agent/README.md` to document the new structure
- [x] run targeted import/path checks for the rewritten contour

## Done when

- `agent/` root contains only control-plane docs/helpers plus clearly justified top-level files
- active file-path references no longer point at the old flat paths
- the root visually reads as intentional instead of as a dumping ground
