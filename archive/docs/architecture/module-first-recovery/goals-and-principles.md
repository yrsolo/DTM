# Goals And Principles

## What we are fixing

We are not optimizing for more interfaces, more wrappers, or prettier folders by themselves.

We are fixing a system where:
- ownership is still easy to lose behind historical technical layers
- the top reading path is thinner than before, but can still drift back into indirection
- product scenarios are not always the first thing the architecture teaches
- old technical paths can still return as "temporary" bridges

## Target state

DTM should read as a module-first system:
- one short top path
- one neutral runtime layer
- one obvious owning module per active scenario
- explicit read/write/publication model
- narrow inter-module contracts, intents, and jobs instead of semantic cross-module glue

## Hard principles

### Scenario first
Architecture boundaries must be justified by real user or operational scenarios, not by SDKs, handlers, or helper packages.

### Module first
Every meaningful change starts with one question:
which owning module should this scenario belong to?

### Runtime is neutral
`platform.runtime` may classify, dispatch, orchestrate, invalidate, and observe.
It may not become the home of attachment, reminder, rendering, snapshot, or access business rules.

### One obvious path
Normal reading path:
- entrypoint
- runtime routing
- module public surface
- module-local builder/use case

If understanding a scenario requires following bridge after bridge, the architecture is still wrong.

### Old path must die
No new path counts unless the old path is removed, demoted, or explicitly deprecated with a removal task.

### Cache is aftermath, not glue
Modules publish invalidation intents or aftermath signals.
They do not directly know or clean another module's cache internals.

### Folder structure must teach
`src` should visually teach ownership, not archaeology.
