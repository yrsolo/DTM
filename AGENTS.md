# AGENTS

## Purpose
Operational rules for AI agents working in this repository.

## Scope
- Applies to the whole repository unless overridden by a deeper `AGENTS.md`.
- If user instruction conflicts with this file, user instruction has priority.

## Working Mode
- Main working branch: `dev`.
- Never push directly to `main` without explicit user approval.
- Keep changes small, reversible, and testable.
- Do not delete files/folders without explicit user approval.

## Mandatory Iteration Status
After each meaningful iteration, agent must report:
1. Current status (`in progress` / `blocked` / `done`).
2. Is it ready to commit? (`yes/no` with reason).
3. Proposed commit message (if ready).
4. Is it ready for merge/push to `main`? (`yes/no` with reason).
5. Documentation status (`updated/not needed`) with affected files.

Use this template:
- `Status: ...`
- `Ready to commit: yes/no`
- `Proposed commit message: ...`
- `Ready for main: yes/no`
- `Docs status: updated/not needed (...)`

## Quality Gate Before Commit
- Changed code runs for relevant flow (`run_timer.cmd` for timer changes).
- No obvious secret leaks in changed files.
- Docs updated when behavior/config/architecture/process changed.

## Documentation Freshness (Mandatory)
- If code/config/process changes, update relevant docs in the same change set.
- At minimum check:
  - `README.md` (project positioning/behavior level),
  - `doc/01_*`, `doc/02_*` (current behavior/modules),
  - `doc/03_*` (backlog and status),
  - `doc/09_git_workflow.md` (process rules), if workflow changed.
- For merge/push to `main`, stale documentation is a blocker.
- If docs are intentionally unchanged, agent must state why (`not needed` with reason).

## Safety
- Never print or expose secrets from `.env`, key files, tokens, proxy credentials.
- Respect `.gitignore` and security docs.
