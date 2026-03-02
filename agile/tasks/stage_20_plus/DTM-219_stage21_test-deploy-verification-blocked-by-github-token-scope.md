# DTM-219: Stage 21 test deploy verification blocked by GitHub token scope

## Context
- API fix `DTM-218` is merged to `dev` and pushed (`a588235`).
- Test API domain still returns old `dtm_runtime_noop` response.
- Cloud check shows test gateway points to function `dtm` (`d4e81vgi5vri8poe7qba`) with old `$latest` version.

## Goal
- Deploy `dev` revision with DTM-218 fix to test contour and verify domain response.

## Blocker
- Automatic workflow dispatch from local console is blocked:
  - GitHub API response: `403 Resource not accessible by personal access token`.
- Owner action is required to run workflow manually in GitHub UI.

## Required owner action
1. Open GitHub Actions workflow `Deploy Yandex Cloud Function (test contour)`.
2. Click `Run workflow`.
3. Set `git_ref=dev`, run, and confirm success.

## Verification steps after deploy
- `https://dtm-api-test.solofarm.ru/api/v1/frontend/doc` should return HTML page.
- `https://dtm-api-test.solofarm.ru/api/v1/frontend?statuses=work,pre_done&limit=10&include_people=true` should return `dtm_frontend_api_payload`.

## Work log
- 2026-03-02: Verified live test domain still returns old noop payload.
- 2026-03-02: Verified gateway binding and function target (`dtm-api-test -> d4e81vgi5vri8poe7qba`).
- 2026-03-02: Checked function versions; latest tag precedes fix commit rollout.
- 2026-03-02: Attempted workflow dispatch via GitHub API from local env token; got `403` due token scope.

## Links
- `.github/workflows/deploy_yc_function_main.yml`
- `index.py`
- `agile/tasks/stage_20_plus/DTM-218_stage21_api-http-method-fallback-hotfix.md`
