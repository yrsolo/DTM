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

## 2) Jira Runtime Rules
1. Jira is mandatory for execution lifecycle.
2. No execution without Jira key, unless owner gave explicit waiver:
   `LOCAL_ONLY_MODE until <date>`.
3. Required lifecycle per task:
   - create/confirm issue,
   - move to `В работе` before code changes,
   - comment with evidence,
   - move to `Готово` on completion.

## 3) Freshness And Trust Gate
1. Text docs are hypotheses until checked against runnable/code artifacts.
2. Update `agile/context_registry.md` with trust/evidence before decomposition.
3. If source trust is `low`, execution is blocked until verification task is done.

## 4) Owner Escalation Rules
1. Any wait-state is blocked-state.
2. Immediate Telegram notification is mandatory via `agent/notify_owner.py`.
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
- `Jira: done/blocked (...)`
