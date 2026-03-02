# DTM-221: Stage 21 frontend API event-shape hardening and Actions requirements split

## Context
- API on test domain still returned runtime noop for frontend routes.
- Event shape from gateway can vary significantly (`rawPath`, `params.path.proxy`, `rawQueryString`, `method`, `ANY`).
- GitHub workflows installed full `requirements.txt` while smoke checks use only stdlib modules.

## Goal
- Harden frontend API route detection against mixed HTTP event shapes.
- Keep planner trigger gate unchanged for non-API calls.
- Split lightweight Actions dependencies into dedicated file.

## Non-goals
- No production rollout mode change.
- No deploy runtime package reduction (function package still uses `requirements.txt`).

## Plan
1. Expand HTTP event detection in `_extract_payload`.
2. Expand path extraction (`rawPath`, `requestContext.path`, `params.path.proxy`, `url`).
3. Expand query extraction from `rawQueryString`.
4. Keep `ANY -> GET` normalization for read-only frontend routes.
5. Add `requirements.actions.txt` and switch both workflows pre-smoke install to it.

## Checklist (DoD)
- [x] Hardened parser for method/path/query/event-shape implemented.
- [x] Local smoke on multiple event shapes returns frontend API artifacts, not noop.
- [x] Separate Actions requirements file added.
- [x] Test/prod workflows use `requirements.actions.txt` for pre-smoke install.
- [ ] Cloud verification pending test deploy.

## Work log
- 2026-03-02: Updated `index.py` with broad event-shape parsing for HTTP detection and routing.
- 2026-03-02: Local smoke confirms `dtm_frontend_api_payload` for `ANY + proxy path`, `rawPath`, and URL-based events.
- 2026-03-02: Added `requirements.actions.txt`; updated deploy/release workflows to install it instead of full `requirements.txt`.

## Links
- `index.py`
- `requirements.actions.txt`
- `.github/workflows/deploy_yc_function_main.yml`
- `.github/workflows/release_yc_function_prod.yml`
