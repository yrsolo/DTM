# Stage 14 Tracking Policy Convergence

Date: 2026-02-28
Key: `DTM-163`

## Scope
Converge repository process rules to one policy:
- Jira is preferred but not mandatory.
- Local tracking in `agile/sprint_current.md` and `agile/tasks/*.md` is valid execution control.
- Iteration status must report `Tracking: done/blocked (...)`.

## Why
Previous rules mixed mandatory-Jira and local-first practices, causing overhead and confusion.

## Changes
- Updated control-plane section in `AGENTS.md`.
- Updated runtime contract in `agent/OPERATING_CONTRACT.md`.
- Updated TeamLead protocol/prompt references to tracking-neutral language.
- Updated sprint notes to remove mandatory-Jira statement.

## Verification
- Process documents contain no blocker rule "no execution without Jira key".
- Iteration template consistently uses `Tracking` field.
- Sprint board notes reflect optional Jira model.

## Residual Risk
Historical task files may still contain old Jira-only wording; this does not block execution.