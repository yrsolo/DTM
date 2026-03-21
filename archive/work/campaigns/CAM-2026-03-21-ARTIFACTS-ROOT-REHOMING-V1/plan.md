# CAM-2026-03-21-ARTIFACTS-ROOT-REHOMING-V1

## Goal

Remove the repo-root `artifacts/` output shelf and rehome active generated outputs under `work/artifacts/`.

## Scope

- root `artifacts/`
- active defaults in `agent.artifacts/*`, reminder tooling, and bootstrap fallback
- workflow excludes and tests that still point to the old root

## Non-goals

- no archival of active artifact scripts
- no change to production business behavior

## Tasks

- [x] verify `artifacts/` is output/tooling state rather than runtime code
- [x] move active defaults from `artifacts/` to `work/artifacts/`
- [x] update workflow excludes and tests
- [x] migrate existing local output files and remove root `artifacts/`
- [x] run targeted checks and close tracking

## Done when

- active code and workflows no longer point at root `artifacts/`
- current local generated outputs live under `work/artifacts/`
- repo root no longer contains `artifacts/`
