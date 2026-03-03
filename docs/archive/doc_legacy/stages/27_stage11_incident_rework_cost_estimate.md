# Stage 11 Incident And Rework Cost Estimate

## Scope
Estimate repeated cost from delivery incidents across stages 9-10 where evidence is explicit.

## Method (Heuristic)
- Unit of cost: focused recovery block (analysis + fix + verification + redeploy), not calendar day.
- Inputs:
  - Jira task logs (`DTM-83`, `DTM-84`, `DTM-92`),
  - deploy run failures and retries,
  - blocker/rollback notes in sprint/backlog docs.
- Scale:
  - Low: <= 0.5 block,
  - Medium: ~1 block,
  - High: >= 2 blocks.

## Estimated Repeated Cost
| incident pattern | occurrences | estimated cost | notes |
|---|---:|---:|---|
| Missing/invalid runtime contour (env/secret/service account) | 3 | High | produced repeated deploy/runtime failures before stabilization |
| Late detection after deploy (instead of preflight/contract gate) | 2 | Medium | reduced after contract smoke + preflight introduction |
| Lifecycle/process friction around blocked states | 2 | Low-Medium | mitigated by immediate Telegram escalation and sprint blocked section |

## Interpretation
- Largest cost driver was configuration/runtime drift.
- Second driver was late failure detection (now partially reduced by new gates).
- Process friction exists but has lower direct recovery cost than runtime contour failures.

## Use In Next Slice
- Prioritize corrective backlog by highest repeated-cost cluster first:
  1) runtime contour hardening,
  2) earlier failure detection,
  3) process friction cleanup.
