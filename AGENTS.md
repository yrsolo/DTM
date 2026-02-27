# AGENTS

## Purpose
Operational rules for AI agents working in this repository.

## Runtime Contract (Mandatory)
- Primary runtime control document: `agent/OPERATING_CONTRACT.md`.
- Every agent session must start with contract read and explicit confirmation:
  - `CONTRACT CHECK: OK`
- If contract check is missing, execution/planning must not continue.

## Scope
- Applies to the whole repository unless overridden by a deeper `AGENTS.md`.
- If user instruction conflicts with this file, user instruction has priority.

## Working Mode
- Main working branch: `dev`.
- Never push directly to `main` without explicit user approval.
- Keep changes small, reversible, and testable.
- Do not delete files/folders without explicit user approval.

## Jira Is Mandatory Control Plane
- Jira is the default source of execution state (task creation, status transitions, assignment, comments with evidence).
- Any execution task must have a Jira key before implementation starts.
- If Jira access is unavailable, agent must immediately escalate owner and request one of:
  - restore Jira access, or
  - explicit temporary waiver: `LOCAL_ONLY_MODE until <date>`.
- Without Jira access or explicit waiver, execution work is blocked.

## Autonomous Commits
- Agent may create small safe commits in `dev` without waiting for user confirmation when all are true:
  - scope is local and low-risk (docs, tooling config, non-breaking refactor, isolated bugfix),
  - relevant smoke-check passed,
  - no schema/storage migration,
  - no secrets/security-sensitive edits.
- Agent must still report commit summary and proposed next action.
- Merge/push to `main` always requires explicit user approval.

## Mandatory Iteration Status
After each meaningful iteration, agent must report:
1. Current status (`in progress` / `blocked` / `done`).
2. Is it ready to commit? (`yes/no` with reason).
3. Proposed commit message (if ready).
4. Is it ready for merge/push to `main`? (`yes/no` with reason).
5. Documentation status (`updated/not needed`) with affected files.
6. Jira update status (`done/blocked`) with concrete actions (created issue, status changed, comment added).

Use this template:
- `Status: ...`
- `Ready to commit: yes/no`
- `Proposed commit message: ...`
- `Ready for main: yes/no`
- `Docs status: updated/not needed (...)`
- `Jira: done/blocked (...)`

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

## Source Trust And Freshness (Mandatory)
- Text docs are hypotheses, not guaranteed truth, until verified against runnable artifacts.
- Before task decomposition, agent must perform a freshness check:
  - compare docs with current code paths/scripts/config used by real flow,
  - check recent repository changes (`git log`/`git blame`) for drift,
  - confirm whether validations/smoke checks still represent current behavior.
- Agent must record trust status in `agile/context_registry.md`:
  - `source`, `last_verified_at`, `verified_by`, `evidence`, `trust_level` (`high/medium/low`), `notes`.
- If trust level is `low` for a source required by current task, do not start execution tasking; create a clarification/verification task first.

## Safety
- Never print or expose secrets from `.env`, key files, tokens, proxy credentials.
- Respect `.gitignore` and security docs.

## Owner Decision Escalation
- If progress is blocked and owner input is required, mark task as blocked and notify owner.
- Preferred command:
  - `python agent/notify_owner.py --title "Decision required" --details "<question>" --options "1) ...; 2) ..." --context "<task/branch>"`
- Waiting for owner/agent reply is treated as blocked by default; notification is mandatory immediately.
- Every escalation message must include explicit next action for owner:
  - `1) create a new chat for <task>`
  - `2) reply to TeamLead that task is ready / continue current chat`
- Telegram notification language: Russian only.
- Telegram notification style: include one suitable emoji in title/details (for example `🚨` for blockers, `✅` for completion, `❓` for decision).

## Mandatory Escalation Cases
- Business behavior ambiguity (two valid product outcomes).
- Destructive operations (delete/move large modules, history rewrite, force push).
- Security-sensitive operations (credential rotation, access scope changes).
- Any change that can impact production flow or external costs.
- Any state where execution stops because agent is waiting for response (from owner or another agent).
