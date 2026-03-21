# Legacy Archaeology Notes

Moved on: 2026-03-04

Modules moved from `core/` to `old/v1/`:
- `people.py`
- `planner.py`
- `repository.py`
- `use_cases.py`

Why moved:
- these files were compatibility shims from previous architecture waves,
- active runtime no longer depended on them,
- owner decision: keep as legacy artifacts, not as active code.

Usage rules:
- read-only reference,
- no new runtime dependencies,
- any future migration should target `src/*` modules directly.
