# Publication States

## Canonical ladder

Attachment publication should be understood through these states:

1. `mutation accepted`
2. `processing`
3. `publication-ready`
4. `published in primary read-model`
5. `visible to browser after refetch`

## State meaning

### 1. Mutation accepted
- upload contract accepted
- direct upload completed or `finalize` accepted
- attachment exists in the mutation flow

This is not publication.

### 2. Processing
- metadata validation, preview, conversion, or background work is still running

This is not publication.

### 3. Publication-ready
- attachment is technically ready to appear in the read-model
- runtime can now coordinate stale marking, invalidation, or refresh

This is still not final browser success.

### 4. Published in primary read-model
- `snapshot` has projected the attachment into the primary task-list read-model

This is the backend publication milestone.

### 5. Visible to browser after refetch
- frontend receives a readiness signal
- frontend refetches the main task-list payload
- attachment appears in that updated payload

This is the final user-visible success state.

## Hard rules

- `finalize` is not equal to `published`
- terminal job success without projection into the primary task-list payload is not complete success
- readiness/status is an operational signal between processing/publication readiness and browser refetch
- user-visible success is measured only at `visible to browser after refetch`
