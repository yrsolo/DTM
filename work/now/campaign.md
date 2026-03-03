# CAM-DOC-REFORM-TEXTS

## Goal
Hard split repository texts into two clean contours: `docs/` for system documentation and `work/` for delivery process.

## Scope
- Build the new `work/{archive,now,roadmap}` map.
- Move process artifacts out of system docs.
- Keep legacy materials archived with preserved git history.

## Non-goals
- Deep semantic rewrite of old stage documents.
- Runtime logic refactoring.

## Definition of Done
- Root README points to `docs/` and `work/` entrypoints.
- `docs/README.md` is a system-doc map only.
- `work/README.md` is a process map only.
- Current and roadmap process data are readable without `agile/` dependency.

## Risks
- Broken links after large moves.
- Mixed references in legacy documents.
