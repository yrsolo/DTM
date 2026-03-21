# Archive

Historical material lives here and stays outside the active `src/`, `docs/`, and `work/` trees.

## Structure

- `archive/code/` - archived runtime and legacy code paths
- `archive/docs/` - archived documentation and retired architecture/process material
- `archive/work/` - archived campaigns, plans, evidence, and legacy execution artifacts
- `archive/legacy_test_refs/` - reference-only legacy test snippets kept outside the default test contour

Examples:

- `archive/code/old/` - pre-recovery legacy source tree moved out of the repo root
- `archive/code/scripts/` - one-off historical migration helpers no longer part of the active script set
- `archive/work/notebooks/` - exploratory notebooks moved out of the active repo root

## Rule

- Active runtime and active documentation must not depend on archive paths.
- New historical material should be archived here instead of being left inside active trees.
