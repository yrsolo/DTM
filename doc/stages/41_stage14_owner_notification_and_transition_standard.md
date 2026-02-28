# Stage 14 Owner Notification and Transition Standard

Date: 2026-02-28
Keys: `DTM-164`, `DTM-165`

## Scope
Standardize owner communication in two areas:
1. Telegram notification intent.
2. Stage transition summary format.

## Notification Semantics
- `blocked`: owner action required, work paused.
- `info`: informational update, work continues autonomously.

`agent/notify_owner.py` now supports:
- `--mode blocked`
- `--mode info`

Alert evaluator notifications are sent in `info` mode to avoid false blocker signals.

## Stage Transition Summary (Mandatory)
At stage boundary, TeamLead must provide:
1. What was completed in previous stage and why it matters.
2. What will be executed in next stage and why it is needed.
3. Initial next-stage task estimate.
4. Explicit owner confirmation request (`go/no-go`).

## Verification
- Smoke checks pass for notify payload and alert evaluator flow.
- Process docs include stage-transition requirement.