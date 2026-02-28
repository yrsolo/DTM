# Stage 15 Ops Checklist Refresh

Date: 2026-02-28
Key: `DTM-170`

## Scope
Updated cloud deployment smoke checklist with:
- deploy readiness gate command,
- render freshness command and pass/fail criterion,
- evidence template extension for freshness result.

## Updated File
- `doc/ops/stage9_deployment_smoke_checklist.md`

## Why
Previous checklist validated status codes and health, but not guaranteed that the task diagram had been freshly rendered in Google Sheet.

## New Operator Signal
If corner timestamp is stale (for example, around two hours old), smoke must fail and deployment is not accepted as operationally ready.