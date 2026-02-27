# DTM-76: TSK-079 Stage 9 kickoff main auto-deploy workflow for Yandex Cloud Function

## Context
- Stage 8 is closed (`done 6 / remaining 0`).
- Owner requested automatic function deployment on `main` updates.
- Runtime entrypoint exists in repository (`index.handler`).

## Goal
- Add CI workflow that deploys Cloud Function on `push` to `main`.
- Document required owner inputs and one-time cloud setup.

## Non-goals
- No production cutover policy change beyond main-branch deploy trigger.
- No function business-logic refactor.

## Plan
1. Add GitHub Actions workflow for deploy-on-main.
2. Document required repository variables and setup steps.
3. Sync sprint/context/backlog docs.
4. Run smoke checks for workflow/docs consistency.

## Checklist (DoD)
- [x] Workflow file added under `.github/workflows`.
- [x] Stage 9 setup document added with owner inputs.
- [x] Sprint/context docs synchronized.
- [x] Jira lifecycle completed with evidence.

## Work log
- 2026-02-27: DTM-76 created and moved to `V rabote`.
- 2026-02-27: Added `deploy_yc_function_main.yml` and `doc/ops/stage9_main_autodeploy_setup.md`.
- 2026-02-27: Updated sprint/context/README/backlog links for Stage 9 kickoff.

## Links
- Jira: DTM-76
- Setup doc: `doc/ops/stage9_main_autodeploy_setup.md`
