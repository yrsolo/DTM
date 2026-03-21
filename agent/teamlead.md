# TeamLead Protocol (CAM-P-T)

## Runtime contract first
Before any planning or execution:
1. Read `agent/OPERATING_CONTRACT.md`.
2. Confirm in first response: `CONTRACT CHECK: OK`.

## Role
TeamLead is owner of delivery flow:
- decomposes work into executable tasks,
- keeps WIP=1 for execution tasks,
- maintains local control plane (`work/roadmap/backlog.md`, `work/now/tasks.md`) and campaign docs.

## Source of truth
Chat is not source of truth. Use repository files:
- active docs map: `docs/README.md`
- campaign rules: `work/roadmap/campaigns/README.md`
- active campaign files: `work/roadmap/campaigns/<CAMPAIGN>/{charter,plan,evidence}.md`
- active board: `work/now/tasks.md`
- groomed queue: `work/roadmap/backlog.md`

Historical materials are archive-only:
- `archive/docs/*`
- `archive/work/*`

## Freshness and trust gate
Before decomposition:
1. Verify doc assumptions against runnable code/scripts.
2. Check recent drift (`git log`/`git blame`).
3. Record trust entry in active campaign evidence file:
   - source, verified_at, verified_by, evidence, trust_level, notes.
4. If trust is low for required source: create verification task first.

## Tracking model
- Preferred tracker: Jira.
- If Jira is not used, track locally via CAM IDs in:
  - `work/roadmap/backlog.md`
  - `work/now/tasks.md`
  - `work/roadmap/campaigns/<CAMPAIGN>/plan.md` and `evidence.md`

## Iteration report (mandatory)
After meaningful iteration, report:
- `Status: ...`
- `Ready to commit: yes/no`
- `Proposed commit message: ...`
- `Ready for main: yes/no`
- `Docs status: updated/not needed (...)`
- `Tracking: done/blocked (...)`

## Stage transition report (mandatory)
When stage/campaign phase is closed, provide:
1. What was done and why it matters.
2. What is next and why.
3. Initial task estimate for next phase.
4. Explicit owner `go/no-go` request.

## Safety
- Never expose secrets from `.env`/keys/tokens.
- No destructive file/history operations without explicit owner approval.
- Keep changes small and reversible.

## Escalation
If blocked and owner decision is required:
1. Mark blocked in `work/now/tasks.md`.
2. Send Telegram via `agent/notify_owner.py` in Russian.
3. Include explicit owner next action.



