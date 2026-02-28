# DTM-92: Stage 10 cloud shadow-run evidence with required PROTOTYPE S3 keys

## Context
- Stage 10 requires a real cloud-profile shadow-run evidence artifact.
- Required-mode gate is implemented, but execution needs `PROTOTYPE_*_S3_KEY` values.

## Goal
- Execute cloud shadow-run with `--require-cloud-keys` and store resulting evidence artifact.

## Non-goals
- No fallback to skipped cloud check.
- No lockbox/env contour redesign in this task.

## Plan
1. Verify `PROTOTYPE_*_S3_KEY` presence in active runtime contour.
2. Run `agent/stage8_shadow_run_evidence.py --require-cloud-keys`.
3. Record artifact path and command logs in docs/Jira.

## Checklist (DoD)
- [x] Jira key exists (`DTM-92`) and moved to `В работе`.
- [x] Required keys are present.
- [x] Cloud shadow-run command succeeded in required mode.
- [x] Evidence artifact path recorded.
- [x] Jira evidence comment added.
- [x] Jira moved to `Готово`.
- [x] Telegram completion sent.

## Work log
- 2026-02-27: Created Jira issue `DTM-92`, moved to `В работе`.
- 2026-02-27: Executed required-mode command; result `shadow_run_failed_checks=missing_required_cloud_keys`.
- 2026-02-27: Added Jira evidence comment about blocker and sent owner escalation via `agent/notify_owner.py`.
- 2026-02-27: Uploaded baseline artifacts to Object Storage, configured `PROTOTYPE_*_S3_KEY`, reran required-mode shadow run successfully.
- 2026-02-27: Evidence artifact: `artifacts/shadow_run_stage8/20260227T215711Z_stage8_shadow_run/shadow_run_evidence.json`.

## Links
- Jira: DTM-92
- Command:
  - `.venv\Scripts\python.exe agent\stage8_shadow_run_evidence.py --require-cloud-keys`
