# Success Criteria

The program is complete only when all are true:

- active code reads through `entrypoint -> platform.runtime -> owning module`
- the main browser read-side is obviously the primary task-list payload with embedded card data and attachments
- readiness/status is clearly treated as an operational signal, not as the canonical read-side artifact
- attachment publication is understood as visibility in that primary read-model
- publication states are explicitly understood through mutation -> processing -> publication-ready -> published -> visible after refetch
- `platform.runtime` is not the hidden brain of the project
- each active module reads as a real ownership center, not a wrapper over a historical cluster
- cache invalidation no longer justifies semantic cross-module coupling
- a new engineer can open entrypoint, one module facade, and one module builder and understand the scenario in under a minute
- Telegram remains available without distorting the main architecture priorities
