# Stage 16 Execution Plan

## Objective
Expand reminder LLM runtime to support provider selection (`openai`, `google`, `yandex`) without changing reminder orchestration contract.

## Baseline
- Stage 16 estimate baseline: 5 tasks.
- Dynamic tracking rule: after each completed task update `Done` and `Remaining` in `agile/sprint_current.md`.
- Current counter: done `5`, remaining `0`.

## Stage 16 slices
1. `DTM-172`: kickoff and bounded queue.
2. `DTM-173`: runtime adapter expansion (OpenAI/Google/Yandex).
3. `DTM-174`: provider bootstrap smoke coverage.
4. `DTM-175`: docs and runbook refresh for provider contour.
5. `DTM-176`: stage closeout and Stage 17 handoff.

## Delivery rules
- WIP stays 1 active execution task.
- Jira is optional; local tracking in `agile/sprint_current.md` + `agile/tasks/*.md` is the active control plane.
- Telegram completion notes use `info` mode while execution continues; `blocked` only when execution is paused waiting for owner.

## Exit criteria
- Runtime provider selection works for all three providers.
- Local smoke verifies adapter selection mapping.
- Docs and backlog/context artifacts reflect new provider contour.
