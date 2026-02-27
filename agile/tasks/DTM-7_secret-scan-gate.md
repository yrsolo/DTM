# DTM-7: Secret scan pre-commit gate hardening and verification

## Context
- Stage 0.5 requires stable secret-scan gate before publication.
- `detect-secrets` hook exists, but docs and evidence flow needed explicit full-repo verification command.

## Goal
- Confirm and document a repeatable full-repo secret-scan verification path.

## Non-goals
- No key rotation in this task.
- No history rewrite.

## Mode
- Execution mode

## Plan
1) Verify current pre-commit detect-secrets configuration.
2) Add explicit full-repo scan command to project docs/process.
3) Run smoke-check and record evidence in Jira/agile docs.

## Checklist (DoD)
- [x] Full-repo detect-secrets smoke command is documented.
- [x] Security docs no longer state this gate as pending.
- [x] Smoke-check command passes in virtualenv.
- [x] Jira lifecycle/comments updated with evidence.

## Work log
- 2026-02-27: Jira issue DTM-7 created and moved to `V rabote`.
- 2026-02-27: Updated docs (`README`, `doc/07`, `doc/03`) to reflect active Stage 0.5 gate.
- 2026-02-27: Installed `pre-commit` in `.venv` for local gate verification.
- 2026-02-27: Smoke-check passed: `.venv\Scripts\python.exe -m pre_commit run detect-secrets --all-files` -> `Passed`.
- 2026-02-27: Jira evidence comment added; issue transitioned to `Gotovo`.

## Links
- Jira: DTM-7
- Notes: doc/03_reconstruction_backlog.md (section 0.5)
