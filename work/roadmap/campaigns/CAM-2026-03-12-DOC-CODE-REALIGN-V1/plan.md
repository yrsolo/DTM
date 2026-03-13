# CAM-2026-03-12-DOC-CODE-REALIGN-V1

## Goal

Realign active docs to verified runtime code and the accepted 2026-03-12 architecture direction so agents stop following stale system stories.

## Scope

Required focus:
- `README.md`
- `docs/system/architecture.md`
- `docs/system/architecture_values.md`
- `docs/system/module_map.md`
- active runtime/metrics docs affected by the new wave
- browser auth/masked/full contract in main docs
- active main-wave brief in `work/roadmap/`

## Concrete tasks

1. Build a drift matrix from active code vs active docs.
2. Mark transitional modules explicitly as transitional.
3. Mark frozen modules explicitly as frozen.
4. Remove stale YDB-first and planner-centric canonical stories.
5. Import browser auth contract into main docs without making `agent/intructions/**` a living doc root.
6. Promote architecture values into the main policy/doc layer as a canonical normative document.
7. Add explicit cross-links from `README.md`, `docs/system/architecture.md`, `docs/system/module_map.md`, and the active main-wave brief.

## Acceptance criteria

- active docs tell one coherent current-state story
- planner runtime is labeled transitional
- frozen Telegram/reminder status is documented
- browser auth/masked/full contract exists in main docs
- `docs/system/architecture_values.md` exists in the main tree as canonical values doc
- values no longer live only in imported reference materials
- agents can treat architecture values as governing policy rather than discussion notes
