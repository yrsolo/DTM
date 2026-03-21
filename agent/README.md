# Agent Utilities

`agent/` contains local operator and agent support utilities for this repo.

## What lives here

- `OPERATING_CONTRACT.md` - mandatory runtime contract for every agent session
- `notify_owner.py` - blocked/completion notification helper
- one-off operational scripts and smokes used during rollout, verification, and evidence collection
- `intructions/` - owner-provided planning/reference inputs; these are not execution tracking
- `tmp_run_logs/` - disposable local run logs, not part of the tracked architecture story

## What does not live here

- active system docs: `docs/`
- execution tracking and campaigns: `work/`
- active runtime/application code: `src/`
