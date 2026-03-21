# CAM-2026-03-21-AGENT-HYGIENE-POLISH-V1 Evidence

## Trust Gate

- source: current `agent/` tree, helper-script import graph, and `agent` docs/prompts
  - last_verified_at: `2026-03-21`
  - verified_by: `Codex`
  - evidence:
    - `Get-ChildItem agent -Recurse -Depth 2`
    - `rg -n "src\\.legacy|src\\.adapters\\.|src\\.services\\.|docs/archive|work/archive" agent scripts`
    - `Get-Content agent/README.md`
    - `Get-Content agent/teamlead.md`
    - `Get-Content agent/teamlead_chat_prompt.md`
  - trust_level: `high`
  - notes: current inspection shows the active code map is already cleaner than the `agent/` contour: several harnesses still point at removed roots and at least one prompt doc is visibly mojibake.

## Active Tasks

- [x] rewire active maintenance helpers to current module paths
- [x] archive stale legacy-bound smokes out of the active `agent/` root
- [x] clean `agent` docs/prompts and archive references
- [x] verify targeted imports/smokes

## Iteration Notes

- campaign opened after accepting the remaining `src/core/` shared slice and switching the next polish focus from architecture to repo-surface hygiene.
- active maintenance helpers `agent/migrations/backfill_milestones_versions.py` and `agent/migrations/migrate_milestones_to_v.py` still pointed at removed `src.adapters.ydb.*` imports at campaign start.
- `agent/teamlead_chat_prompt.md` was mojibake and still referenced `docs/archive/*` / `work/archive/*`.
- archived legacy-bound smokes under `archive/work/agent/legacy_smokes/`:
  - `llm_provider_bootstrap_smoke.py`
  - `reminder_sli_summary_smoke.py`
  - `reminder_enhancer_counters_smoke.py`
  - `render_adapter_smoke.py`
  - `sync_hash_gate_smoke.py`
- targeted verification passed:
  - `python -c "from agent.migrations.backfill_milestones_versions import BackfillStats; from agent.migrations.migrate_milestones_to_v import MigrationStats; print('agent_maintenance_imports_ok')"`
  - `python -m agent.smokes.group_query_smoke`
  - `python scripts/check_no_legacy_entrypoint_imports.py`
  - `rg -n "src\\.legacy|src\\.services\\.|src\\.adapters\\.|docs/archive|work/archive" agent`
