# CAM-2026-03-21-ATTACHMENTS-MODULE-FIRST-FLOW-V1 Evidence

## Trust Gate

- source: current active attachment mutation/publication path
  - last_verified_at: `2026-03-21`
  - verified_by: `Codex`
  - evidence:
    - `src/contexts/attachments/public.py`
    - `src/contexts/attachments/module.py`
    - `src/contexts/attachments/internal/*`
    - `tests/contexts/attachments/*`
  - trust_level: `high`
  - notes: direct code inspection confirmed the residual smell is the public `get_*_job` grammar in `attachments/public.py`.

## Active Tasks

- [x] verify the current smell against active code
- [x] replace public/module job grammar with one module-owned flow surface
- [x] align tests
- [x] record closeout verdict

## Closeout

- before: `attachments` still exposed the scenario through `get_attach_task_file_job`, `get_delete_task_attachment_job`, `get_cleanup_task_attachments_job`, and `get_generate_attachment_preview_job`.
- after: the module now exposes one `AttachmentCommandFlow` in `attachments.application`, and the public surface routes queue handlers through that flow instead of job-shaped entry names.
- verification:
  - `python -m unittest tests.contexts.attachments.test_attach_task_file_job tests.contexts.attachments.test_delete_task_attachment_job tests.contexts.attachments.test_cleanup_task_attachments_job tests.contexts.attachments.test_generate_attachment_preview_job tests.architecture.test_guardrails_v0 tests.entrypoints.test_import_safety -v`
  - `rg -n "get_attach_task_file_job|get_delete_task_attachment_job|get_cleanup_task_attachments_job|get_generate_attachment_preview_job" src tests`
- next worst smell: `snapshot` still reads as a module surface wrapped around `build_snapshot_engine` and thin capability proxies.
