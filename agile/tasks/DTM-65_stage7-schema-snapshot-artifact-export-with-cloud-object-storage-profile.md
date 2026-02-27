# DTM-65: TSK-068 Stage 7 schema snapshot artifact export with cloud Object Storage profile

## Context
- Stage 7 policy (`doc/15`) sets Object Storage as primary artifact backend for serverless runtime.
- Existing artifact flow exports `quality_report`, `alert_evaluation`, and `read_model`, but no dedicated schema snapshot artifact for consumer compatibility checks.

## Goal
- Add deterministic `schema_snapshot` artifact generation from read-model.
- Support local file export and cloud-profile Object Storage upload path.

## Non-goals
- No fixture bundle generation (handled in next task).
- No mandatory cloud upload in local dev flow.

## Plan
1. Add schema snapshot builder module.
2. Extend local launcher flags for schema snapshot file and Object Storage key export.
3. Extend baseline capture to include `schema_snapshot.json`.
4. Update docs and stage counters.

## Checklist (DoD)
- [x] `schema_snapshot` builder added and deterministic.
- [x] `local_run.py` supports `--schema-snapshot-file`.
- [x] Cloud profile upload path available via `--schema-snapshot-s3-key`.
- [x] Baseline helper emits `schema_snapshot.json`.
- [x] Docs and sprint/task records aligned.
- [x] Smoke checks passed in `.venv`.

## Work log
- 2026-02-27: DTM-65 created and moved to `V rabote`.
- 2026-02-27: Implemented `core/schema_snapshot.py` and launcher integration.
- 2026-02-27: Added baseline flow integration and smoke script `agent/schema_snapshot_smoke.py`.
- 2026-02-27: Updated Stage 7 docs and counters (`done 3 / remaining 4`).

## Links
- Jira: DTM-65
- Policy: `doc/15_stage7_read_model_consumer_policy.md`
- Stage plan: `doc/14_stage7_execution_plan.md`
