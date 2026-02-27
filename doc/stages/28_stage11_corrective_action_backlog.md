# Stage 11 Corrective Action Backlog

## Priority A (runtime contour hardening)
1. Enforce required runtime variable contract at deploy preflight (including `PROTOTYPE_*_S3_KEY` in dedicated profile).
   - Owner: TeamLead
   - Target: Stage 12 / first slice
   - Verification: deploy run fails fast with explicit message when contract is incomplete.
2. Add lockbox sync validation report (`required keys present` + version id).
   - Owner: TeamLead
   - Target: Stage 12 / first slice
   - Verification: CI artifact contains lockbox validation section.

## Priority B (earlier failure detection)
3. Extend pre-deploy gate with object-storage read probe in non-destructive mode.
   - Owner: TeamLead
   - Target: Stage 12 / second slice
   - Verification: workflow step emits `object_storage_probe_ok`.
4. Add daily automatic smoke scheduler (health + dry-run timer) with persisted report.
   - Owner: Owner + TeamLead
   - Target: Stage 12 / second slice
   - Verification: daily report artifact appears without manual trigger.

## Priority C (process friction reduction)
5. Add lightweight Jira helper script for transition/comment template reuse.
   - Owner: TeamLead
   - Target: Stage 12 / third slice
   - Verification: task lifecycle operations reduced to one command preset.
6. Add sprint counter consistency check script (`Done/Remaining` vs task statuses).
   - Owner: TeamLead
   - Target: Stage 12 / third slice
   - Verification: mismatch exits non-zero and reports offending items.

## Priority D (operational onboarding)
7. Publish single “operator start page” linking quickstart, rollback, smoke, evidence report.
   - Owner: TeamLead
   - Target: Stage 12 / closeout
   - Verification: one-page runbook exists and is referenced in `README.md`.
