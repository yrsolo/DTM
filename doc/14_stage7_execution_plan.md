# Stage 7 Execution Plan

## Objective
Start implementation-ready migration planning after Stage 6, so the first web visualization prototype can consume stable read-model artifacts without ad-hoc parsing.

## Baseline
- Stage 7 estimate baseline: 7 tasks.
- Dynamic tracking rule: after each completed task update `Done` and `Remaining` in `agile/sprint_current.md`.
- Current counter: done `5`, remaining `2`.

## Stage 7 slices (initial)
1. TSK-066 (DTM-63): kickoff and estimate baseline.
2. TSK-067 (DTM-64): read-model consumer compatibility policy + serverless artifact storage contour (Object Storage primary).
3. TSK-068 (DTM-65): exported schema snapshot artifact for frontend integration checks (Object Storage in cloud profile).
4. TSK-069 (DTM-66): frontend-friendly static fixture bundle from baseline captures (Object Storage in cloud profile).
5. TSK-070 (DTM-67): UI migration spike scope and acceptance checklist.
6. TSK-071: shadow-run readiness checklist for visualization data consumer.
7. TSK-072: Stage 7 closeout and Stage 8 handoff package.

## Delivery rules
- WIP stays 1 active execution task.
- Every task must have Jira lifecycle: create/confirm key, `V rabote` before changes, evidence comments, `Gotovo` after completion.
- On each task completion, send owner Telegram completion note with stage counter (`done/remaining`).

## Exit criteria
- Stage 7 queue is fully documented and Jira-aligned.
- Consumer-facing read-model integration policy is explicit and testable.
- Artifacts needed for Stage 8 prototype work are reproducible from environment-aware flow (`local artifacts` for dev, `Object Storage` for serverless).
