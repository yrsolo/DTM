# Agile Strategy

## Objective
Deliver DTM to stable production operation with clear, maintainable process artifacts.

## Current Focus (Stage 21)
1. Split release contour: test auto-deploy vs manual prod release.
2. Stabilize API/domain contour for test (`dtm-api-test`) and prod (`dtm-api`).
3. Keep release docs/runbooks concise and trustworthy.

## Delivery Rules
- WIP=1 for execution tasks.
- Jira is optional; local control plane is `agile/sprint_current.md` + `agile/tasks/**`.
- Every stage ends with clear closeout and next-stage go/no-go.

## Constraints
- Preserve current business behavior in production contour.
- No secrets in git or console output.
- Small, reversible changes with smoke evidence.

## Metrics
- Deployment smoke pass rate.
- Reminder delivery SLI stability.
- Lead time from task start to done.
