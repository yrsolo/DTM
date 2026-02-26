# Contributing

## Branching
- `main`: stable, production-like state.
- `dev`: default branch for development.
- Optional: `feature/*` for isolated tasks, merged into `dev`.
- `hotfix/*` from `main` for urgent fixes.

## Standard Flow
1. Start from latest `dev`.
2. Implement one logical change.
3. Run relevant checks (at minimum, scenario-level smoke test).
4. Commit with clear message.
5. Merge into `dev`.
6. Merge `dev -> main` only after approval and smoke verification.
7. Push branches.

## Commit Message Style
- Imperative, short, specific.
- Examples:
  - `fix timer crash on empty timing`
  - `split source and target sheet configuration`
  - `refresh docs for git workflow`

## Merge to Main Criteria
- Feature works in real flow.
- No regressions in target output sheets.
- No secrets in diff.
- Docs are updated for behavior/config changes.

## Hotfix Flow
1. Branch from `main`: `hotfix/<topic>`.
2. Implement minimal safe fix.
3. Merge to `main`, push.
4. Merge `main` back to `dev`.

