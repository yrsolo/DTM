# Job Status Schema

## Purpose

`src/platform/runtime/worker/status_store.py` is the operational source of truth for recent command executions.

It supports:

- `/info`
- hidden admin status endpoint `/admin/jobs/{job_id}`
- retry/terminal failure visibility
- recent-history debugging without full log search

## Record shape

Required fields:

- `job_id`
- `command_type`
- `status`
- `requested_at_utc`

Optional fields:

- `started_at_utc`
- `finished_at_utc`
- `requested_by`
- `summary`
- `warnings`
- `retryable`
- `error`

## Status values

Current canonical statuses:

- `accepted`
- `running`
- `success`
- `failed_retryable`
- `failed_terminal`

Legacy stored values may still exist in older objects/history, but new writes must use the canonical set above.

## Meanings

### `accepted`

Command was accepted by intake and written to job status store before worker execution.

### `running`

Worker has started handling the command.

### `success`

Command finished successfully.

### `failed_retryable`

Command finished with a transient failure and queue-driven retry is expected.

### `failed_terminal`

Command finished with a terminal failure and should not be retried by transport.

## Summary vs error

### `summary`

Short structured data safe for operator UI:

- render counters
- notify counters
- target sheet info
- snapshot summary fields

### `error`

Short structured failure data:

- `code`
- `message`
- optional bounded technical fields

No secrets and no large payload dumps.

## Storage layout

Current S3 status store layout:

- `jobs/{env}/status/{job_id}.json`
- `jobs/{env}/latest/{command_type}.json`
- `jobs/{env}/history/index.json`
- `jobs/{env}/history/by-command/{command_type}.json`

## Retention

Current short-history policy:

- last `50` jobs overall
- last `20` jobs per command type

This is enough for `/info` and short operational investigations. It is not intended to replace long-term logs.
