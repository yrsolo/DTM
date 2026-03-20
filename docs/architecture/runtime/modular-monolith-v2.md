# Modular Monolith V2

> Superseded on 2026-03-20 by `docs/architecture/module-first-recovery/README.md`.
> Keep this file as historical precedent for the previous modular-monolith wave, not as the current normative canon.

This document is the normative master text for the DTM modular-monolith refactor wave.

It supersedes chat memory as the working architectural brief for future campaign starts. When future campaign plans need the target shape, migration order, or boundary rules, start here.

## Goal and scope

Goal:
- make the active runtime visually and structurally clearer
- reduce coupling between runtime transport, orchestration, and business logic
- prepare the codebase for possible future service extraction without pretending to be microservices today

Scope:
- active runtime code and architecture docs
- campaign sequencing and ownership rules for the refactor wave
- boundary rules for new `entrypoint`, `platform`, and `contexts` structure

Out of scope for this kickoff:
- full implementation of the target package structure
- immediate removal of all transitional code
- redesign of frozen operational areas beyond what is required for clean ownership

## First-class top-level architecture

DTM target shape for this wave is:

- `entrypoint`
  - thin request/event intake only
  - parse input, classify mode, delegate to platform or context facade, translate result
- `platform`
  - runtime classification, worker intake, queue dispatch, trigger orchestration, config/bootstrap, low-level infrastructure wiring
  - no business/domain logic
- `contexts`
  - first-class business modules with explicit ownership and public facades

Target top-level package map:

```text
src/
  entrypoint/
  platform/
  contexts/
    snapshot/
    rendering/
    reminders/
    telegram_interaction/
    attachments/
    access_api/
```

## Six first-class contexts

### `snapshot`
- owns ingestion, normalization, state build/update, and prepared read-side state

### `rendering`
- owns timeline/designers representation generation and writeback flows

### `reminders`
- owns reminder selection, payload building, styling, and delivery orchestration

### `telegram_interaction`
- owns Telegram webhook intake, update parsing, update-to-command mapping, and Telegram interaction flows

### `attachments`
- owns attachment upload/finalize/preview/delete/read lifecycle and attachment access policy

### `access_api`
- owns frontend-facing HTTP surface, masked/open access policy, and browser-safe DTO assembly

## Migration order

The canonical migration order for this refactor wave is:

1. architectural contract and ownership map
2. skeleton `src/entrypoint`, `src/platform`, `src/contexts`
3. thin `handler.py` and explicit mode routing
4. queue worker routing by command ownership
5. controlled bootstrap transition
6. minimal architecture guardrails
7. trigger orchestration
8. `attachments` as the first fully extracted context
9. `reminders`
10. `snapshot`
11. `rendering` with enforced boundary to `snapshot`
12. `telegram_interaction`
13. `access_api`
14. target config centralization
15. legacy archive and final polish

`attachments` remains the first fully extracted context. Early bootstrap and guardrails move ahead of it as enabling rules, not as a replacement for it.

## Controlled bootstrap transition

Bootstrap transition policy for this wave:

- the existing bootstrap may stay as a transitional composition root
- the old bootstrap may delegate only; it must not become the new architectural center
- each newly introduced context must have its own `module.py`
- new contexts must not be born through centralized ad-hoc wiring in one growing global bootstrap file
- context-local builders may be lazy, but ownership must remain inside the context

## Early architecture guardrails

These guardrails must be planned and introduced before the first full context extraction:

- no deep cross-context imports
- no `os.getenv()` outside allowed config/bootstrap points
- no active imports from `legacy` or archive-only runtime code
- entrypoint modules must not import heavy adapters directly
- mode routing tests
- command routing tests
- import-boundary tests
- `os.getenv` grep/test gate
- active-path no-legacy-import gate
- snapshot/rendering boundary test

## Ownership rules

Ownership rules for this wave:

- top-level architecture is context-first, not transport-first
- `jobs`, `worker`, `http`, `triggers`, `telegram SDK`, `ydb`, `s3`, `llm` are not first-class business modules; they are runtime/platform or adapter concerns
- platform-owned surfaces must be documented explicitly:
  - healthcheck
  - info/admin ops
  - queue status / job status surfaces
  - observability / runtime diagnostics
- command ownership must be explicit and documented
- route ownership must be explicit and documented
- `group_query_reply` belongs to `telegram_interaction`

## Explicit invariants

The following invariants are mandatory:

- thin entrypoint only
- platform/runtime contains no business logic
- no mega-bootstrap
- each new context must have its own `module.py`
- no deep imports into another context’s internals
- queue routing uses explicit `match/case`
- mode routing uses explicit `match/case`
- `group_query_reply` belongs to `telegram_interaction`
- `rendering` depends only on `snapshot.public` or snapshot contracts
- direct snapshot-internal imports from rendering are forbidden
- early guardrails are mandatory before first full context extraction
- `attachments` remains the first fully extracted context

## Start-of-campaign rule

Before opening any child campaign or implementation wave:

1. read `docs/architecture/runtime/modular-monolith-v2.md`
2. read the relevant ownership docs
3. verify against current code paths
4. update campaign `evidence.md` trust gate
5. only then decompose tasks

## Canonical reading order

Future campaign starts should use this reading order:

1. `docs/architecture/runtime/modular-monolith-v2.md`
2. `docs/architecture/runtime/context-ownership-map.md`
3. `docs/architecture/runtime/command-ownership-v2.md`
4. `docs/architecture/runtime/route-ownership-v2.md`
5. `docs/architecture/runtime/trigger-orchestration-v2.md`
6. `docs/architecture/runtime/bootstrap-discipline-v2.md`
7. `docs/architecture/runtime/guardrails-v2.md`
8. relevant `docs/modules/<context>.md`
9. current code paths and current campaign `evidence.md`
