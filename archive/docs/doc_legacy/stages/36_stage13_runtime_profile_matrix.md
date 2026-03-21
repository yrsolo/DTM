# Stage 13 Runtime Profile Matrix and Guardrails

Date: 2026-02-28
Task: `DTM-159`

## Objective
Normalize runtime profile expectations and hard guardrails for local, dry-run, and cloud invocation contours.

## Runtime Matrix
| profile | trigger path | external calls | required config | primary check |
|---|---|---|---|---|
| local dry-run | `local_run.py --dry-run --mock-external` | disabled/mocked | local `.env` contour | `agent/read_model_publication_smoke.py` |
| local sync-only | `local_run.py --mode sync-only` | Google Sheets read path | sheets creds + sheet names | `agent/stage8_shadow_run_evidence_smoke.py` |
| cloud healthcheck | function invoke with health payload | none (minimal path) | function env + secrets mapping | `agent/invoke_function_smoke.py --healthcheck` |
| cloud timer dry-run | function invoke mode `timer` + dry-run | optional depending on flags | deploy workflow vars + Lockbox bindings | stage9 smoke checklist |
| cloud shadow-run required | `stage8_shadow_run_evidence.py --require-cloud-keys` | Object Storage reads | `PROTOTYPE_*_S3_KEY` trio | `agent/stage8_shadow_run_evidence_smoke.py` |

## Guardrails
- Every runtime-affecting change must declare target profile(s).
- Dry-run and mock-external must stay available for safe validation.
- Cloud required-mode checks cannot be bypassed silently.
- Failure mode must provide actionable error category (config/runtime/dependency).

## Operator Notes
- Prefer deterministic smoke before any cloud deploy.
- Keep runtime profile assumptions in task evidence comments.
- When profile behavior changes, update runbook/checklist in same change set.
