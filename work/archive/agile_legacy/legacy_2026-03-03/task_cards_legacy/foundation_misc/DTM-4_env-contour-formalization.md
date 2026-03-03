# DTM-4: Env contour formalization (`ENV`, `.env.dev`, `.env.prod`)

## Context
- Stage 0 backlog requires explicit dev/test/prod contour.
- Current env usage exists but policy and split files are not formalized.

## Goal
- Define and document environment contour with safe defaults for local work.
- Prepare non-breaking path for `.env.dev` / `.env.prod` usage.

## Non-goals
- No secret rotation.
- No production deployment changes.

## Mode
- Execution mode

## Plan
1) Audit current env variable usage and defaults.
2) Introduce explicit contour docs and example files policy.
3) Apply minimal code/config changes only if required for safe mode selection.

## Checklist (DoD)
- [x] ENV contour documented and unambiguous.
- [x] `.env.example` aligned with contour approach.
- [x] No secret leakage and no production behavior regression.
- [x] Jira comment/status updated with evidence.

## Work log
- 2026-02-27: Jira issue DTM-4 created and moved to `В работе`.
- 2026-02-27: Added runtime contour loader (`ENV` + optional `.env.<ENV>`) in `config/constants.py`.
- 2026-02-27: Added optional safety enforcement `STRICT_ENV_GUARD` for dev/test source-target split.
- 2026-02-27: Added `.env.dev.example` and `.env.prod.example`.
- 2026-02-27: Updated README and docs (`doc/01`, `doc/02`) with env contour policy.
- 2026-02-27: Smoke-check passed in virtualenv (`config.constants` import and `local_run.py --help`).

## Links
- Jira: DTM-4
- Notes: agile/sprint_current.md
