# CAM-2026-03-21-BOOTSTRAP-READABILITY-V1 Plan

Smell:
- `src/platform/bootstrap.py` still looks slightly heavier than the beauty standard for neutral runtime glue

Target ideal:
- bootstrap remains a composition root and stable runtime seam, but visually reads like neutral glue rather than a mini control center

Kill criteria:
- `index.py` no longer exposes bootstrap mutation seams or eager app-context access
- runtime tests and entry helpers consume explicit platform getters instead of mutable top-level globals
- `src/platform/bootstrap.py` reads as neutral lazy runtime glue, not a mini control center

Completed changes:
- replaced `APP_DEPS` / `APP_TRIGGERS` with explicit runtime getters
- removed the `_get_app_context()` seam from `index.py`
- kept lazy shell/context getters only where they still express real runtime boundaries
