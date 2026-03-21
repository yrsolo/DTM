# Guardrails V2

This document defines the first minimal architecture guardrails required early in the modular-monolith refactor wave.

Governing source:
- [../module-first-recovery/README.md](../module-first-recovery/README.md)

## Early mandatory rules

- no deep cross-context imports
- no `os.getenv()` outside allowed config/bootstrap points
- no active imports from `legacy` or archive-only code
- entrypoint must not import heavy adapters directly

## Planned early checks

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

These guardrails should be introduced before the first fully extracted context so migration velocity does not silently recreate the old coupling pattern.

Current enforced baseline in the active runtime:
- active runtime paths may not import `src.legacy`
- active runtime paths may not import `archive.code.legacy_runtime`
- active runtime paths may not import the legacy `config` package
- default tests may not import legacy or archived-legacy namespaces

