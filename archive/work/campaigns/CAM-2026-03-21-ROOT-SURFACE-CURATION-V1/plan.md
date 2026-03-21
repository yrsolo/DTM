# CAM-2026-03-21-ROOT-SURFACE-CURATION-V1

## Goal

Clean the remaining misleading repo-root surface without forcing active roots into worse homes.

## Scope

- physical dead roots at repo top level
- root-level explanatory docs for justified non-`src` active directories
- tracking updates for the resulting repo map

## Non-goals

- no redesign of production runtime
- no relocation of `web_prototype/` into `src/`
- no relocation of generated `artifacts/` into archive

## Tasks

- [x] verify whether root `core/` is still a live code root or only dead leftovers
- [x] remove physical dead roots and caches from repo top level
- [x] document why `artifacts/` and `web_prototype/` intentionally remain at repo root
- [x] align root tracking with the resulting repo surface

## Done when

- dead physical roots are gone
- justified root directories have a clear README
- root README links explain the remaining special-purpose roots
