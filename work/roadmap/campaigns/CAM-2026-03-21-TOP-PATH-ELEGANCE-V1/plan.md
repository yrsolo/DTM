# CAM-2026-03-21-TOP-PATH-ELEGANCE-V1 Plan

Smell:
- the top path is already short, but `index.py` still carries a small amount of ceremonial glue that makes the first jump feel explained rather than inevitable

Target ideal:
- `index.py -> src/entrypoint/handler.py -> one shell` reads as the obvious system entry path

Kill criteria:
- no eager app-context access remains in the top path
- no stale glue helpers remain in `index.py`
- `index.py` reads as a thin entrypoint, not a relay with ceremony

Scope boundary:
- `index.py`
- `src/entrypoint/handler.py`
- the smallest necessary supporting runtime/doc/test files around this path

Non-goals:
- no routing redesign
- no shell behavior change
- no bootstrap redesign beyond what is required for top-path readability
- no naming cleanup outside the top-path contour

## Tasks

### P01 - Verify the active top-path contour
- `CAM-2026-03-21-TOP-PATH-ELEGANCE-V1-P01-T001` verify the current top path in code and active docs with a trust-gated evidence record
- `CAM-2026-03-21-TOP-PATH-ELEGANCE-V1-P01-T002` confirm the exact smell and pass/fail kill criteria against `index.py`, `src/entrypoint/handler.py`, and the runtime glue they depend on

### P02 - Remove top-path ceremony
- `CAM-2026-03-21-TOP-PATH-ELEGANCE-V1-P02-T001` remove eager app-context access or stale helper seams from `index.py` where they no longer buy clarity
- `CAM-2026-03-21-TOP-PATH-ELEGANCE-V1-P02-T002` keep `src/entrypoint/handler.py` as the single obvious top router without adding new ceremony

### P03 - Sync docs, checks, and closeout
- `CAM-2026-03-21-TOP-PATH-ELEGANCE-V1-P03-T001` update the smallest active docs needed so the top-path story matches the code
- `CAM-2026-03-21-TOP-PATH-ELEGANCE-V1-P03-T002` run a short smoke/guard check and record a short verdict: before, after, next worst thing
