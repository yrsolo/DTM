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
- [x] Merge `dev -> main` completed.
- [x] Push to `origin/main` completed.
- [x] Jira evidence comment added.
- [x] Jira moved to `Gotovo`.
- [x] Telegram completion sent.

## Work log
- 2026-02-27: Created `DTM-83`, moved to `V rabote`.
- 2026-02-27: `dev -> main` merge pushed (`main` head `99594fa`), GitHub Actions deploy run started.
- 2026-02-27: Deploy workflow run `22499553371` failed on `Deploy function version` with error `No credentials`; task moved to blocked pending cloud auth setup decision.
- 2026-02-27: Owner provided temporary service-account JSON secret (`YC_SA_JSON_CREDENTIALS`); workflow switched to secret-based credential path for immediate deploy recovery.
- 2026-02-27: Workflow fix merged to `main` (`1c3e4b9`), deploy run `22500598734` completed with `success`.

## Links
- Jira: DTM-83
- Workflow: `.github/workflows/deploy_yc_function_main.yml`
