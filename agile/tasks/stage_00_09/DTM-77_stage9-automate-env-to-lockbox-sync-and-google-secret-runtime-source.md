# DTM-77: TSK-080 Stage 9 automate .env to Lockbox sync and Google secret runtime source

## Context
- Owner requested to avoid manual secret copy and upload full `.env` contour into Lockbox.
- Cloud runtime should accept Google key as text secret payload instead of repository file dependency.

## Goal
- Add repeatable script to sync all `.env` keys to Lockbox (`DTM`) and include `GOOGLE_KEY_JSON` from local key file.
- Switch runtime Google key sourcing to secret text env (`GOOGLE_KEY_JSON` / `GOOGLE_KEY_JSON_B64`) with local file fallback.

## Non-goals
- No production function rollout in this task.
- No changes to business logic flows.

## Plan
1. Add Lockbox sync utility script.
2. Add runtime key-source fallback in `config/constants.py`.
3. Run smoke and execute sync command.
4. Sync sprint/docs/context and close Jira lifecycle.

## Checklist (DoD)
- [x] `.env` -> Lockbox sync script added.
- [x] Runtime supports Google key text secret source.
- [x] Lockbox sync command executed successfully.
- [x] Sprint/docs/context/Jira synchronized.

## Work log
- 2026-02-27: DTM-77 created and moved to `V rabote`.
- 2026-02-27: Added `agent/sync_lockbox_from_env.py` and `GOOGLE_KEY_JSON` runtime source fallback.
- 2026-02-27: Executed Lockbox sync via script and verified payload keys in current secret version.

## Links
- Jira: DTM-77
