# CAM-2026-03-21-CORE-ROOT-UNIFICATION-V1

## Why

The repo hygiene pass exposed one remaining architectural lie in the active code map: runtime code, tests, and smokes still import the legacy root `core/` package even though the active `src/` tree already has `src/core/` as the canonical domain home.

As long as both roots stay alive, the repo keeps telling two incompatible stories about where domain logic lives.

## Smell

The active contour still splits domain reality between the stale root `core/` package and the canonical `src/core/` package.

## Target Ideal

All active domain code lives under `src/core/`, and every active import path reads that truth directly.

The root `core/` package must disappear as an active Python root.

## Kill Criteria

1. active runtime code imports `src.core.*`, not `core.*`
2. active tests and maintained agent smokes import `src.core.*`, not `core.*`
3. the root `core/` tracked Python package no longer exists as an active code root
4. guardrails fail if root `core.*` imports or files quietly return
5. targeted contour tests stay green

## Scope Boundary

- `src/core/**` and the legacy root `core/**`
- active runtime/test/agent/script imports
- tracking and architecture guardrails

## Non-Goals

- no broad redesign of the internal domain API shape beyond path unification
- no new domain abstraction wave unrelated to the root/package split
