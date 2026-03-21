# CAM-2026-03-21-AGENT-ROOT-CURATION-V1 Evidence

## Trust Gate

- source: current `agent/` tree and live file-path references across workflows/docs/helpers
  - last_verified_at: `2026-03-21`
  - verified_by: `Codex`
  - evidence:
    - `Get-ChildItem agent`
    - `rg -n "agent/[A-Za-z0-9_./-]+\\.py|agent\\\\[A-Za-z0-9_./\\\\-]+\\.py|python -m agent\\.[A-Za-z0-9_]+" README.md docs work scripts .github tests src web_prototype local_run.py agent`
  - trust_level: `high`
  - notes: the root `agent/` contour is still visually flat even after the previous hygiene pass; multiple distinct helper families are active and referenced by exact file paths, so this wave must move files and rewrite those references together.

## Active Tasks

- [x] regroup active agent helpers into role-true subfolders
- [x] rewrite live path references
- [x] refresh root agent docs
- [x] verify targeted execution paths

## Iteration Notes

- root regrouping plan uses these active shelves:
  - `agent/deploy/`
  - `agent/prototype/`
  - `agent/artifacts/`
  - `agent/migrations/`
  - `agent/reminders/`
  - `agent/smokes/`
- historical one-off generator `build_stage12_audit_matrix.py` moved out of the active root into `archive/work/agent/historical_tools/`.
- root `agent/` now keeps only:
  - `OPERATING_CONTRACT.md`
  - `notify_owner.py`
  - `README.md`
  - `teamlead.md`
  - `teamlead_chat_prompt.md`
  - active role-true subfolders
- targeted verification passed:
  - `python -m agent.deploy.prepare_prod_release --help`
  - `python -m agent.prototype.prepare_web_prototype_payload_smoke`
  - `python -m agent.artifacts.stage8_shadow_run_evidence_smoke`
  - `python -m agent.smokes.group_query_smoke`
  - `python -c "from agent.migrations.backfill_milestones_versions import BackfillStats; from agent.migrations.migrate_milestones_to_v import MigrationStats; print('agent_migrations_imports_ok')"`
  - `rg -n "python agent/(deploy|prototype|artifacts|reminders|smokes|migrations)/|agent/(deploy|prototype|artifacts|reminders|smokes|migrations)/[A-Za-z0-9_./-]+\\.py" README.md docs work scripts .github tests src web_prototype local_run.py agent`
