# Attachments

## Purpose

`attachments` is the first fully extracted context in the modular-monolith refactor wave.

It owns the attachment lifecycle end-to-end:
- request upload
- direct upload contract handoff
- finalize
- metadata publication
- preview lifecycle
- delete lifecycle
- cleanup lifecycle
- view / download / read access policy

## Public facade expectation

Target context shape:

```text
src/contexts/attachments/
  public.py
  module.py
  contracts/
  application/
  domain/
  adapters/
```

External callers should use the context facade only, not internal files.

## Allowed dependencies

- `platform` transport/runtime shells
- shared contracts/utilities kept intentionally small
- storage/object adapters owned by the context
- snapshot public contracts only where publication/read-side interaction is necessary

## Forbidden dependencies

- deep imports into another context’s internals
- ownership leakage into generic runtime/worker modules
- direct transport logic as the place where business rules live

## Commands owned

- `attach_task_file`
- `delete_task_attachment`
- `cleanup_task_attachments`
- `generate_attachment_preview`

## Routes owned

- attachment request-upload paths
- attachment finalize paths
- attachment delete paths
- attachment read/view/download paths

## Transitional extraction notes

- current implementation is spread across HTTP handlers, jobs, services, and snapshot-engine-facing pieces
- preserve current behavior first, then consolidate into one context facade
- `attachments` remains the first full extraction target after early bootstrap discipline and guardrails are in place

