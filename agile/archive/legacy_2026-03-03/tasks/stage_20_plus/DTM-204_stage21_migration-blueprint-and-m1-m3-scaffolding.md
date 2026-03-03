# DTM-204: Stage 21 migration blueprint and M1-M3 scaffolding

## Context
- Need a concrete, readable migration program from current architecture to layered target architecture.
- Need atomic staged plan and standards before deep refactor work.
- Need initial code scaffolding for M1-M3 without breaking current runtime.

## Goal
- Add complete migration documentation package under `docs/*`.
- Add initial code skeleton in `src/*` for:
  - domain contracts + normalization interface (M1),
  - service/handler split boundaries (M2),
  - source hash gate primitives (M3).
- Update README with architecture/migration section and current migration checklist.

## Non-goals
- No runtime switch to new architecture path yet.
- No full implementation of adapters/store/readmodels integrations.

## Plan
1. Create architecture/plan/tasks/contracts/standards docs.
2. Add `src/core` and adjacent skeleton modules.
3. Update active sprint/context docs and README links.
4. Run compile smoke to validate skeleton imports.

## Checklist (DoD)
- [x] `docs/architecture/target-architecture.md` created.
- [x] `docs/migration/plan.md` created.
- [x] `docs/migration/tasks.md` created with atomic tasks.
- [x] `docs/contracts/data-contracts.md` created with JSON examples.
- [x] `docs/standards/engineering-standards.md` created.
- [x] `src/core` scaffold created (models/normalize/rules).
- [x] M2/M3 skeleton modules added (`services`, `handlers`, `hash_gate`).
- [x] README updated with architecture/migration links and current checklist.
- [x] Smoke check passed.

## Work log
- 2026-03-02: Added migration doc package under `docs/`.
- 2026-03-02: Added scaffolding under `src/` with core contracts, normalize interface, and hash gate skeleton.
- 2026-03-02: Updated README with migration references/checklist.

## Links
- `docs/architecture/target-architecture.md`
- `docs/migration/plan.md`
- `docs/migration/tasks.md`
- `docs/contracts/data-contracts.md`
- `docs/standards/engineering-standards.md`
- `src/core/models/contracts.py`
- `src/core/normalize/interface.py`
- `src/services/sync/hash_gate.py`
- `README.md`
