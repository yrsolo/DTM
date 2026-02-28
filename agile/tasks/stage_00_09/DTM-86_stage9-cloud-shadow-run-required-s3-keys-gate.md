# DTM-86: Stage 9 cloud shadow-run required S3 keys gate

## Context
- Stage 8 shadow-run builder allows cloud check to be skipped when `PROTOTYPE_*_S3_KEY` env values are absent.
- Stage 9 needs explicit cloud-profile pass/fail criteria, not soft skip.

## Goal
- Add required mode for cloud shadow-run where missing `PROTOTYPE_*_S3_KEY` values fail execution.
- Cover this behavior in smoke checks and operational checklist.

## Non-goals
- No migration of object storage adapter implementation.
- No UI/prototype behavior changes.

## Plan
1. Extend `agent/stage8_shadow_run_evidence.py` with `--require-cloud-keys`.
2. Update smoke test to validate required-mode failure on missing keys.
3. Update Stage 9 ops checklist with cloud gate command and expected outcome.
4. Record evidence in Jira and sprint docs.

## Checklist (DoD)
- [x] Jira key exists (`DTM-86`) and moved to `В работе`.
- [x] Shadow-run builder supports required cloud-keys mode.
- [x] Smoke test covers required-mode fail behavior when keys are absent.
- [x] Ops checklist documents required-mode command.
- [x] Jira evidence comment added.
- [x] Jira moved to `Готово`.
- [x] Telegram completion sent.

## Work log
- 2026-02-27: Created Jira task `DTM-86`, moved to `В работе`.
- 2026-02-27: Added `--require-cloud-keys` gate to shadow-run evidence builder and updated smoke coverage.
- 2026-02-27: Updated Stage 9 deployment smoke checklist with cloud-profile gate step.
- 2026-02-27: Jira evidence comment added; moved to `Готово`; owner completion notification sent via Telegram.

## Links
- Jira: DTM-86
- Files:
  - `agent/stage8_shadow_run_evidence.py`
  - `agent/stage8_shadow_run_evidence_smoke.py`
  - `doc/ops/stage9_deployment_smoke_checklist.md`
