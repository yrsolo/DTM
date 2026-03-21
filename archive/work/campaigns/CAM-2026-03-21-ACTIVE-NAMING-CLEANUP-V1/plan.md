# CAM-2026-03-21-ACTIVE-NAMING-CLEANUP-V1 Plan

Smell:
- active module surfaces and a few access-api aliases still speak with builder- or migration-era wording instead of present-tense ownership language

Target ideal:
- active names and docstrings describe current ownership and role without making the reader translate them mentally from recovery history

Kill criteria:
- no active module docstring says `Local builder` or `used during staged migration`
- access-api snapshot query aliases use query-capability naming instead of broad engine-style naming
- the touched active contour reads in present-tense ownership language

Scope boundary:
- `src/contexts/*/module.py` files in the active contour
- the smallest set of active access-api internal files and tests needed to clarify naming
- the smallest supporting docs/tracking files for closeout

Non-goals:
- no runtime behavior changes
- no module boundary changes
- no broad rename pass across every internal helper in the repo
- no bootstrap or docs-voice cleanup outside this naming smell

## Tasks

### P01 - Verify the smell in active names
- `CAM-2026-03-21-ACTIVE-NAMING-CLEANUP-V1-P01-T001` verify the current active naming smell against module surfaces, access-api handlers, and the beauty audit

### P02 - Remove migration-shaped naming from the active contour
- `CAM-2026-03-21-ACTIVE-NAMING-CLEANUP-V1-P02-T001` rewrite active module docstrings so they describe present ownership
- `CAM-2026-03-21-ACTIVE-NAMING-CLEANUP-V1-P02-T002` rename the smallest set of active access-api capability aliases needed to remove broad `get_snapshot_capability` wording from query-owned paths

### P03 - Verify and close
- `CAM-2026-03-21-ACTIVE-NAMING-CLEANUP-V1-P03-T001` run a short smoke and grep verification
- `CAM-2026-03-21-ACTIVE-NAMING-CLEANUP-V1-P03-T002` record a short verdict: before, after, next worst thing
