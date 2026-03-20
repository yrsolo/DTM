# CAM-2026-03-21-BOOTSTRAP-READABILITY-V1 Plan

Smell:
- `src/platform/bootstrap.py` still looks slightly heavier than the beauty standard for neutral runtime glue

Target ideal:
- bootstrap remains a composition root and stable runtime seam, but visually reads like neutral glue rather than a mini control center

Candidate changes:
- simplify naming or section layout in `src/platform/bootstrap.py`
- reduce ceremony only where stable test seams are preserved or deliberately retired

Current blocker:
- deeper cleanup collides with stable public test seams such as `APP_DEPS`, `APP_TRIGGERS`, `build_runtime_app_context`, and shell getters
- those seams are used directly across active tests and runtime entry helpers, so simplifying bootstrap is no longer a pure readability pass

Blocked decision:
- preserve these seams as accepted bootstrap imperfection and stop here, or
- allow a broader cleanup that rewrites the dependent tests and entry helper expectations
