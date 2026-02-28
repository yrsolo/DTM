# OPERATING CONTRACT (Runtime)

Purpose: single runtime control document for any agent session in this repository.

## 0) Start Gate (Mandatory)
Before any planning or coding, agent must:
1. Read this file (`agent/OPERATING_CONTRACT.md`).
2. Read `AGENTS.md`.
3. Read role file if applicable (for TeamLead: `agent/teamlead.md`).
4. Confirm in first response: `CONTRACT CHECK: OK`.

If step 1-4 is not completed, agent must not continue execution.

## 1) Priority Order
1. Direct owner instruction in current chat.
2. This operating contract.
3. `AGENTS.md`.
4. Role-specific protocol (`agent/teamlead.md`).
5. Other docs (`agile/*`, `doc/*`, `README.md`).

## 2) Task Tracking Runtime Rules
1. Jira is preferred for execution lifecycle, but not mandatory.
2. If Jira is not used, execution lifecycle must be tracked in local files:
   - `agile/sprint_current.md` (Now/Done/Blocked),
   - `agile/tasks/*.md` (plan, work log, evidence).
3. Required lifecycle per task (in Jira or local tracker):
   - register/start task before code changes,
   - record evidence during execution,
   - mark completion with outcome notes.

## 3) Freshness And Trust Gate
1. Text docs are hypotheses until checked against runnable/code artifacts.
2. Update `agile/context_registry.md` with trust/evidence before decomposition.
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
