# Legacy v1 Archive

This folder stores legacy v1 compatibility modules moved out of the active runtime contour.

Purpose:
- keep old code as historical reference (archaeology),
- avoid mixing legacy compatibility shims with active `src/*` runtime modules.

Policy:
- do not import these modules from active runtime paths (`main.py`, `index.py`, `src/*`),
- do not evolve feature behavior here,
- keep only for traceability and rollback analysis.
