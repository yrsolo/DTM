# CAM-2026-03-21-TESTS-ROOT-REALIGNMENT-V1 Evidence

## Trust Gate

| source | last_verified_at | verified_by | evidence | trust_level | notes |
| --- | --- | --- | --- | --- | --- |
| `tests/services` file inventory | 2026-03-21 | Codex | `Get-ChildItem tests/services -File` plus import scan | high | Files mapped cleanly to `contexts`, `entrypoints`, `platform`, and `agent` by their actual imports. |
| target homes | 2026-03-21 | Codex | current file inventory under `tests/contexts`, `tests/entrypoints`, `tests/platform`, `tests/agent` | high | Existing homes already matched the moved test semantics. |

## Changes
- Rehomed `tests/services` files into role-true active test homes.
- Updated the Stage 22 smoke test import to the grouped `agent.smokes` path.
- Removed the old `tests/services` shelf after the move.

## Verification
- `python -m unittest tests.contexts.attachments.test_attachment_policy tests.contexts.access_api.test_readmodel_enums tests.entrypoints.jobs.test_db_migrate_branch_job tests.entrypoints.jobs.test_quality_report_job tests.entrypoints.jobs.test_runtime_context_job tests.entrypoints.jobs.test_task_payloads_job tests.platform.infra.ydb.test_ydb_backoff tests.agent.test_stage22_tri_block_smoke tests.architecture.test_guardrails_v0 -v`
- `Get-ChildItem tests -Directory`

## Outcome
- The test tree now reflects the active ownership map better.
- `tests/services` stopped acting as a compatibility shelf for otherwise well-classified tests.
