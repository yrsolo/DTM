# Guardrails V2

This document defines the active minimal architecture guardrails for the current runtime contour.

Governing source:
- [../module-first-recovery/README.md](../module-first-recovery/README.md)

## Mandatory rules

- no deep cross-context imports
- no `os.getenv()` outside allowed config/bootstrap points
- no active imports from retired or archive-only code
- entrypoint must not import heavy adapters directly

## Baseline checks

- mode routing tests
- command routing tests
- import-boundary tests
- `os.getenv` grep/test gate
- active-path no-legacy-import gate
- snapshot/rendering boundary test
- active-path no-legacy-config-import gate

## Boundary-specific rule

- `rendering` may depend only on `snapshot.public` or snapshot contracts
- direct imports into snapshot internals from rendering are forbidden

## Intent

These guardrails keep the active contour honest: thin entrypoints, explicit boundaries, and no silent return of retired coupling patterns.

Current enforced baseline in the active runtime:
- active runtime paths may not import retired runtime roots or archived code
- active runtime paths may not import the retired root `core` package
- active runtime paths may not import the old flat `config` package
- default tests may not import retired or archived runtime namespaces

