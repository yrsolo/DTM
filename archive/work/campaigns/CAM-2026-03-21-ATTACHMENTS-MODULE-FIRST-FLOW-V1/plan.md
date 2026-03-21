# CAM-2026-03-21-ATTACHMENTS-MODULE-FIRST-FLOW-V1

## Why

`contexts/attachments` exists, but the active public surface still tells the scenario through job-shaped entry names such as:

- `get_attach_task_file_job`
- `get_delete_task_attachment_job`
- `get_cleanup_task_attachments_job`
- `get_generate_attachment_preview_job`

That keeps the module feeling like a well-arranged command/job cluster instead of a single owning attachment flow.

## Smell

`attachments` is still job-shaped instead of module-first flow-shaped.

## Target Ideal

The attachment scenario is read as:

- `contexts.attachments.public`
- one module-owned application flow
- domain/adapters as internal support
- publication aftermath as downstream detail

## Kill Criteria

1. the public/module grammar no longer centers on `get_*_job`
2. one module-owned application flow becomes the obvious way to read attachment mutation/publication
3. jobs remain delivery details, not the main semantic center of the module
4. current attachment behavior and tests remain stable

## Scope Boundary

- `src/contexts/attachments/public.py`
- `src/contexts/attachments/module.py`
- `src/contexts/attachments/application/*` as needed
- `src/contexts/attachments/internal/*` as needed for the first flow cut
- affected attachment tests

## Non-Goals

- no payload/schema changes
- no publication-model redesign across modules yet
- no snapshot ownership rewrite in this wave

## Tasks

- [ ] trust-check the current attachment path against active code
- [ ] replace job-shaped public grammar with one application flow surface
- [ ] align tests to the new owning path
- [ ] record before/after and next worst smell in evidence
