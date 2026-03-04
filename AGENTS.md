# AGENTS.md

Operational rules for AI agents working in this repository.

> Primary runtime control doc: `agent/OPERATING_CONTRACT.md`. It has priority. :contentReference[oaicite:2]{index=2}

## 0) Start gate (mandatory)
At the beginning of every agent session:
1) Read `agent/OPERATING_CONTRACT.md`
2) Read this `AGENTS.md`
3) If role-specific doc is applicable, read it (e.g. TeamLead).
4) First response must include: `CONTRACT CHECK: OK`

If missing, do not proceed.

## 1) Scope and branch rules
- Default working branch: `dev`.
- Never push/merge to `main` without explicit owner approval.
- Keep changes small, reversible, testable.
- Do not delete or move large modules/folders without explicit owner approval.

## 2) Tracking (Jira optional, local tracking required otherwise)
- Jira is preferred but not mandatory.
- If Jira is not used, keep local tracking up to date:
  - `work/now/tasks.md`
  - `work/roadmap/backlog.md`
  - `work/roadmap/campaigns/<CAMPAIGN>/{plan,evidence}.md`

## 3) Commit autonomy (safe commits only)
Agent may create small safe commits on `dev` without waiting for owner approval only if all are true:
- scope is local and low-risk (docs, tooling config, non-breaking refactor, isolated bugfix),
- relevant smoke-check passed,
- no schema/storage migration,
- no secrets/security-sensitive edits.

Merge/push to `main` always requires explicit owner approval.

## 4) Iteration status report (mandatory)
After each meaningful iteration, report:
- `Status: in progress/blocked/done`
- `Ready for main: yes/no`
- `Docs status: updated/not needed (files...)`
- `Tracking: done/blocked (where updated)`

## 5) Freshness & trust gate (mandatory)
Text docs are hypotheses until verified against code/runnable artifacts.
Before decomposing execution tasks:
- compare docs with current runnable paths/scripts/config used by the real flow,
- check drift (recent changes),
- record trust status in campaign evidence:
  - `source`, `last_verified_at`, `verified_by`, `evidence`, `trust_level (high/medium/low)`, `notes`

If trust level is `low` for required sources, do not start execution; create a verification task first.

## 6) Security
- Never print or expose secrets from `.env`, key files, tokens, proxy credentials.
- Respect `.gitignore` and security docs.

---

# Engineering rules to keep the pipeline clean (DTM-specific)

These rules are meant to prevent the pipeline code from drowning in `if` chains, env checks, and scattered error handling.

## 7) No env access outside config/bootstrap
- `os.getenv()` is allowed only in:
  - `src/config/loader.py` (or equivalent config loader)
  - `src/app/bootstrap.py` (composition root)
- `config/constants.py` must not be imported from:
  - `src/services/**`
  - `src/core/**`

Services must receive a typed `cfg` object.

## 8) Thin entrypoints only
Entrypoints (`index.py`, `main.py`) must be thin wrappers:
- parse input
- call one handler/job
- translate result to HTTP response / exit code

Entrypoints must not contain:
- domain rules (normalization, year inference, timing parsing),
- YDB SQL/YQL,
- feature-flag matrices,
- multi-step orchestration logic.

## 9) No feature-flag matrices inside services
Source selection / rollout selection must happen in bootstrap via policy injection:
- choose implementation once,
- pass selected service into use-cases.

Do not introduce:
- `if READMODEL_SOURCE == ...` inside a service,
- `if STORE_MODE == ...` inside a service,
- similar env-driven branching in the core pipeline.

## 10) Core is domain-only
`src/core/**` must contain only domain logic:
- models
- pure functions (normalization, parsing, inference)
- business rules

Forbidden in `src/core/**`:
- external SDK clients (YDB/Sheets/Telegram/OpenAI)
- IO/network calls
- env/config reading

## 11) Bulk reads/writes only (no N+1)
YDB is serverless; quota matters.
Do not introduce query-per-task loops.
Prefer:
- 1 bulk query for tasks
- 1 bulk query for milestones
- 1 upsert for readmodel snapshot

## 12) Error handling boundary
Application services may raise typed errors:
- `TransientError` (retryable/quota/timeouts)
- `PermanentError` (schema mismatch, invalid data, logic bug)
- `UserError` (bad input)

Only entrypoints translate errors to HTTP codes / exit codes.

## 13) Documentation discipline (minimal, focused)
- System documentation lives in `docs/`.
- Development process lives in `work/` (now/roadmap/archive).
- Do not create new doc roots (`doc/`, `documentation/`, etc.)
- If code/config/process changes, update relevant docs in the same change set or explicitly state why docs are unchanged.

## 14) Owner escalation (when blocked or risky)
Escalate to owner when:
- business behavior ambiguity,
- destructive operations (delete/move large modules, history rewrite),
- security-sensitive operations,
- changes impacting production flow or external costs,
- any wait-state (blocked-state).

Follow `agent/OPERATING_CONTRACT.md` escalation procedure. :contentReference[oaicite:3]{index=3}

## Owner Decision Escalation
- If progress is blocked and owner input is required, mark task as blocked and notify owner.
- Preferred command:
  - `python agent/notify_owner.py --mode blocked --title "Decision required" --details "<question>" --options "1) ...; 2) ..." --context "<task/branch>"`
- Waiting for owner/agent reply is treated as blocked by default; notification is mandatory immediately.
- Every escalation message must include explicit next action for owner:
  - `1) create a new chat for <task>`
  - `2) reply to TeamLead that task is ready / continue current chat`
- Telegram notification language: Russian only.
- Telegram notification style: include one suitable emoji in title/details (for example `🚨` for blockers, `✅` for completion, `❓` for decision).

