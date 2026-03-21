# Agent Utilities

`agent/` contains local operator and agent support utilities for this repo.

## What lives here

- `OPERATING_CONTRACT.md` - mandatory runtime contract for every agent session
- `notify_owner.py` - blocked/completion notification helper
- `deploy/` - release, gateway, Lockbox sync, and deploy-smoke helpers
- `artifacts/` - fixture/schema/read-model builders and evidence packagers
- `reminders/` - reminder-specific harnesses and alert evaluators
- `smokes/` - generic active smokes that still validate the live system
- `support/` - small agent-only helper modules used by active operator harnesses
- `owner_inputs/` - owner-provided planning/reference inputs; these are not execution tracking

## What does not live here

- active system docs: `docs/`
- execution tracking and campaigns: `work/`
- active runtime/application code: `src/`
- archived historical harnesses and retired prompts: `archive/work/agent/`

## Hygiene rule

- Active `agent/` files should import only current runtime paths.
- Harnesses that still depend on retired runtime roots or archived-only paths belong in `archive/work/agent/`, not in the active `agent/` root.
- The root `agent/` shelf should stay small: contract files, top-level control helpers, and clearly justified entry files only.
- Grouped agent scripts should be invoked as modules from repo root, for example `python -m agent.deploy.export_deploy_defaults` or `python -m agent.smokes.group_query_smoke`.
