# Yandex Message Queue Setup

## Queues per environment

### Test

- `dtm-test-commands`
- `dtm-test-commands-dlq`

### Prod

- `dtm-prod-commands`
- `dtm-prod-commands-dlq`

## Why DLQ

Main queue processes commands.
DLQ stores poison/problem commands that exceeded retry policy at the queue level.

## Recommended settings

- queue type: `Standard`
- visibility timeout: `60-180s`
- max receive count: `5-10`
- dead-letter queue: matching environment DLQ

## Current trigger topology

Current runtime topology is **not** a separate worker function.

Per environment:

- the same deployed Cloud Function object handles:
  - HTTP gateway events
  - Message Queue trigger events

This document intentionally reflects the current one-function topology.

## Notes

- one trigger per main queue
- queue and trigger must live in the same cloud/folder setup expected by deployment
- queue behavior must match `docs/operations/infrastructure/queue-retry-policy.md`
