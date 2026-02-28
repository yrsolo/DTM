# DTM-85: Stage 9 deployment smoke checklist for Yandex Cloud Function profile

## Context
- Stage 9 auto-deploy is active, but operational post-deploy checks were not formalized as one repeatable checklist.
- Recent incidents showed that health-only check is not enough; timer flow must also be verified.

## Goal
- Publish concise smoke checklist for serverless profile covering:
  - loader health check,
  - timer dry-run path,
  - timer live path,
  - quick failure triage mapping.

## Non-goals
- No runtime architecture changes.
- No alerting/monitoring automation in this task.

## Plan
1. Verify current endpoint behavior on health and timer dry-run paths.
2. Document operational smoke checklist with expected outcomes.
3. Link checklist from Stage 9 deploy setup doc.
4. Update sprint/backlog and Jira evidence.

## Checklist (DoD)
- [x] Jira key exists (`DTM-85`) and moved to `В работе` before doc changes.
- [x] Health and timer dry-run smoke commands verified against current function endpoint.
- [x] Checklist doc created in `doc/ops`.
- [x] Stage 9 deploy setup doc links to new checklist.
- [x] Jira evidence comment added.
- [x] Jira moved to `Готово`.
- [x] Telegram completion sent.

## Work log
- 2026-02-27: Jira issue `DTM-85` created and moved to `В работе`.
- 2026-02-27: Verified endpoint responses:
  - `--healthcheck` => `status_code=200`, `!HEALTHY!`.
  - `--mode timer --dry-run --mock-external` => `status_code=200`, `!GOOD!`.
- 2026-02-27: Added `doc/ops/stage9_deployment_smoke_checklist.md` and linked it from Stage 9 setup doc.
- 2026-02-27: Jira evidence comment added; issue moved to `Готово`; owner completion notification sent via Telegram.

## Links
- Jira: DTM-85
- Endpoint: `https://functions.yandexcloud.net/d4e81vgi5vri8poe7qba`
