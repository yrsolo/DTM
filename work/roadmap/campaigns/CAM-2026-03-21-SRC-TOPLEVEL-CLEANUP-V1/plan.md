# CAM-2026-03-21-SRC-TOPLEVEL-CLEANUP-V1

## Why

`snapshot` architectural cleanup is complete, but the top-level `src/` tree still contains visibly competing historical roots.

Several of those roots no longer hold live Python code, and one active-looking root (`entrypoints_adapters`) survives only as a stray adapter shelf for logic that belongs inside `access_api`.

## Smell

Top-level `src/` still advertises dead or historical roots as if they were active architecture zones, and still keeps one active-looking top-level adapter root that does not own its own scenario.

## Target Ideal

The `src/` root should show only active architecture zones or explicitly justified technical roots.

Dead historical roots and stray adapter shelves must not survive in the active map.

## Kill Criteria

1. dead top-level historical roots no longer appear in the active tree
2. `entrypoints_adapters` no longer exists as a top-level active-looking root
3. moved code now lives inside its owning context
4. guardrails fail if those removed roots quietly return
5. no active imports or tests regress

## Scope Boundary

- top-level `src/` cleanup only
- `work/*` tracking
- architecture guardrails

## Non-Goals

- no broad move of still-active top-level packages beyond the proven stray adapter shelf
- no semantic code rewrites beyond what is needed to remove dead roots and relocate one stray adapter helper into its owning context
