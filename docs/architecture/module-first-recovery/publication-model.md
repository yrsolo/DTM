# Publication Model

## Main rule

Publication success is measured by visibility in the primary task-list read-model.

For attachments, this means:
- file exists in storage: not enough
- upload accepted: not enough
- `finalize` accepted: not enough
- preview or conversion finished: still not enough
- success: attachment appears in the normal browser task-list payload after frontend refetch

## Governing pipeline

`attachments mutation -> platform/runtime invalidation/orchestration -> snapshot projection -> access_api cached delivery`

## Read/write/publication split

### Write side
`attachments` owns upload, finalize, delete, metadata, preview lifecycle, and publication readiness.

### Aftermath
`platform.runtime` owns invalidation intent, refresh coordination, and eventual freshness after mutation.

### Projection
`snapshot` owns turning attachment state into published read-model state.

### Browser delivery
`access_api` owns the cached browser payload that users actually consume.

## Operational meaning

Admin success means:
- job status reaches the right terminal state
- readiness/status reports that the frontend may refetch
- next normal read path returns the attachment in the main task-list payload

Readiness/status endpoint means:
- operational signal for polling
- not the canonical browser read artifact
- not a replacement for publication success

Frontend expectations:
- no heavy rebuild on every open
- normal refetch/polling reaches a fast cached or prepared response
