# OPERATING CONTRACT (Runtime)

Purpose: single runtime control document for any agent session in this repository.

## 0) Start Gate (Mandatory)
Before any planning or coding, agent must:
1. Read this file (`agent/OPERATING_CONTRACT.md`).
2. Read `AGENTS.md`.
3. Confirm in first response: `CONTRACT CHECK: OK`.

If step 1-3 is not completed, agent must not continue execution.

## 1) Priority Order
1. Direct owner instruction in current chat.
2. This operating contract.
3. `AGENTS.md`.
4. Other docs (`docs/README.md`, `work/*`, `README.md`).

## 2) Task Tracking Runtime Rules
1. execution lifecycle must be tracked in local files:
   - `work/now/tasks.md` (Now/Done/Blocked),
   - `work/roadmap/backlog.md` (groomed queue),
   - `work/roadmap/campaigns/<CAMPAIGN>/{plan,evidence}.md` (task breakdown and evidence).
3. Required lifecycle per task:
   - register/start task before code changes,
   - record evidence during execution,
   - mark completion with outcome notes.

## 3) Freshness And Trust Gate
1. Text docs are hypotheses until checked against runnable/code artifacts.
2. Update active campaign evidence file `work/roadmap/campaigns/<CAMPAIGN>/evidence.md` with trust/evidence before decomposition.
3. If source trust is `low`, execution is blocked until verification task is done.

## 4) Owner Escalation Rules
1. Any wait-state is blocked-state.
2. Immediate Telegram notification is mandatory via `agent/notify_owner.py --mode blocked ...`.
3. Notification must be in Russian and include suitable emoji.
4. Notification must contain explicit owner next action.

## 5) No-Parallel Rule
1. Work strictly sequentially (one active execution task).
2. New task starts only after current task is closed or explicitly paused by owner.

## 6) Iteration Report (Mandatory)
After each meaningful iteration, report:
- `Status: ...`
- `Ready to commit: yes/no`
- `Proposed commit message: ...`
- `Ready for main: yes/no`
- `Docs status: updated/not needed (...)`
- `Tracking: done/blocked (...)`

## 7) Stage Closeout Report (Mandatory)
At stage boundary (stage done), report in plain language before entering next stage:
- completed stage summary: what was delivered and why,
- next stage summary: what will be done and why,
- next stage initial task estimate (count),
- explicit owner confirmation request to proceed (`go/no-go`).

## Temporary Owner Authorization (2026-03-22)
Temporary rule for the active repo-finalization phase.

- Owner pre-authorizes sequential execution of bounded cleanup/refactor/polish waves without per-wave confirmation.
- Agent should continue autonomously while all of the following stay true:
  - the direction is already implied by the current owner goals: aesthetics, architectural cleanliness, proportionality, and anti-overengineering;
  - the cut is local or moderately scoped and does not require a business/product choice;
  - the change improves the repo toward a calmer, more canonical shape rather than adding speculative abstraction.
- Agent must stop and escalate only on a real strategic blocker, for example:
  - multiple plausible target architectures with non-obvious long-term consequences,
  - destructive moves affecting large preserved history or externally referenced assets,
  - production/security/cost-sensitive decisions,
  - uncertainty about whether a remaining contour is truly active or should be archived when that cannot be verified from code and runnable artifacts.
- This authorization is temporary and applies only to the current repo-finalization program; keep the note explicit and removable once the repo reaches a stable finished state.


