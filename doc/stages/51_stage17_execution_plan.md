# Stage 17 Execution Plan

## Objective
Allow designers to mention or command the bot in a group chat and receive current tasks or nearest deadlines in that same chat.

## Baseline
- Stage 17 estimate baseline: 5 tasks.
- Dynamic tracking rule: after each completed task update `Done` and `Remaining` in `agile/sprint_current.md`.
- Current counter: done `5`, remaining `0`.

## Stage 17 slices
1. `DTM-177`: kickoff and bounded queue.
2. `DTM-178`: runtime group-query path in cloud handler.
3. `DTM-179`: smoke coverage for parser/render helpers.
4. `DTM-180`: docs and tracking refresh.
5. `DTM-181`: closeout and Stage 18 handoff.

## Exit criteria
- Group commands/mentions are parsed in HTTP webhook payload.
- Bot replies in same group chat with tasks/deadlines summary.
- Local smoke covers parser and renderer behavior.
