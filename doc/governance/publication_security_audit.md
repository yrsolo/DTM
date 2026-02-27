# Security Audit Before Publication

Date: 2026-02-27

## Verified Controls
- `detect-secrets` hook is configured in `.pre-commit-config.yaml` with baseline `.secrets.baseline`.
- `.env` and key files are ignored by git (`.gitignore`).
- Full-repo secret scan command is available and repeatable from virtualenv.

## Required Smoke Command
Run from repository root:

```powershell
.venv\Scripts\python.exe -m pre_commit run detect-secrets --all-files
```

Expected result: `Passed` with no new findings.

## Baseline Management
- Baseline file: `.secrets.baseline`
- Refresh baseline only when intentional changes are reviewed.
- Any baseline refresh must be accompanied by Jira evidence comment.

## Residual Risks
1. Tracked notebooks can still receive accidental secret pastes.
2. Historical leaks in git history require rotation independently from current file state.

## Current Status
- Stage 0.5 gate is active.
- TeamLead evidence flow includes full-repo smoke command output in Jira.
