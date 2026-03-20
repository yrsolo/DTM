# Runtime Canon

## Canonical top path

Normal path:
- `index.py`
- `src/entrypoint/*`
- `src/platform/runtime/*`
- owning module public surface

`index.py` is allowed to be thin and even minimal.
Thin is success here, not a flaw, as long as it is still the obvious start of the scenario.

## Browser read canon

For browser reads, the canonical product path is:
- user requests the main task-list payload
- payload already contains card data and attachments
- `access_api` returns a prepared or cached response
- card/drawer/details UI on the frontend uses this payload instead of defining a separate canonical backend read artifact

Canonical finish line is not:
- upload accepted
- finalize accepted
- readiness endpoint returning `ready` by itself
- opening a separate "card details" pipeline

## Runtime duties only

`platform.runtime` may:
- classify
- dispatch
- orchestrate
- invalidate
- expose ops/diagnostics

It may not:
- absorb module business rules
- become a hidden second bootstrap brain
- become the semantic owner of publication itself
