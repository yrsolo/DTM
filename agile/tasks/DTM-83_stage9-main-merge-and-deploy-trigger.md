# DTM-83: Stage 9 main merge and deploy trigger

## Context
- Owner requested immediate deployment.
- Stage 9 already has deploy workflow prepared; required step is merge `dev` to `main` and push.

## Goal
- Trigger production deploy workflow by pushing current `dev` state to `main`.

## Non-goals
- No feature implementation changes.
- No architecture changes.

## Plan
1. Confirm repository clean state and current branch sync.
2. Run quick smoke sanity command before merge.
3. Merge `dev` into `main` non-interactively.
4. Push `main` to origin to trigger GitHub Actions deploy workflow.
5. Record evidence in Jira and sprint docs.

## Checklist (DoD)
- [x] Jira key exists (`DTM-83`) and moved to `V rabote` before execution.
- [ ] Merge `dev -> main` completed.
- [ ] Push to `origin/main` completed.
- [ ] Jira evidence comment added.
- [ ] Jira moved to `Gotovo`.
- [ ] Telegram completion sent.

## Work log
- 2026-02-27: Created `DTM-83`, moved to `V rabote`.

## Links
- Jira: DTM-83
- Workflow: `.github/workflows/deploy_yc_function_main.yml`
