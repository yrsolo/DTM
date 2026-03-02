# DTM-209: Stage 21 M3 hash basis builder and determinism tests

## Context
- Hash gate needs explicit, deterministic source hash basis before runtime wiring.
- We need executable guarantee that row order does not change hash and data change does.

## Goal
- Add `hash_basis` builder that normalizes selected source fields and sorts by row id.
- Add unit tests for determinism and change sensitivity.

## Non-goals
- No binding to live Google reader yet.
- No production activation of hash gate.

## Plan
1. Add `src/services/sync/hash_basis.py`.
2. Export sync primitives from package boundary.
3. Add tests in `tests/services`.

## Checklist (DoD)
- [x] Hash basis builder committed.
- [x] Determinism test committed.
- [x] Change-sensitivity test committed.
- [x] Full test suite green.

## Work log
- 2026-03-02: Added deterministic hash basis builder.
- 2026-03-02: Added `tests/services/test_hash_basis.py`.
- 2026-03-02: Confirmed test suite and smoke scripts pass.

## Links
- `src/services/sync/hash_basis.py`
- `tests/services/test_hash_basis.py`
