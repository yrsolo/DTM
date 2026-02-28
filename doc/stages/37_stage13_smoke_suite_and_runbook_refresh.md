# Stage 13 Smoke Suite Normalization and Runbook Refresh

Date: 2026-02-28
Task: `DTM-160`

## Objective
Standardize smoke execution tiers and align runbook references to a single operational sequence.

## Smoke Tiers
| tier | intent | commands |
|---|---|---|
| tier-0 syntax | fast import/syntax guard | `python -m compileall agent core config` |
| tier-1 module smoke | validate changed module contract | module-specific `agent/*_smoke.py` |
| tier-2 flow smoke | validate end-to-end contour | `agent/read_model_publication_smoke.py`, `agent/stage8_shadow_run_evidence_smoke.py`, `agent/invoke_function_smoke.py --healthcheck` |

## Runbook Refresh Rules
- Any stage task touching runtime path must record selected smoke tier in Jira evidence.
- Runbook links in docs should point to concise current files, not historical archives.
- If smoke fails due to external contour, classify explicitly (`config`, `dependency`, `runtime`) and capture fallback path.

## Minimal Operator Sequence
1. Run tier-0.
2. Run module-relevant tier-1.
3. For deploy-affecting tasks, run tier-2 before completion.
4. Update sprint/context/backlog along with Jira evidence.
