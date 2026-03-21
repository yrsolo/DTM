# CAM-2026-03-21-SCRIPTS-SURFACE-CURATION-V1 Evidence

## Trust Gate

| source | last_verified_at | verified_by | evidence | trust_level | notes |
| --- | --- | --- | --- | --- | --- |
| `scripts/` file inventory | 2026-03-21 | Codex | `Get-ChildItem scripts -File` | high | Verified the active helper script set from the current worktree. |
| script usage references | 2026-03-21 | Codex | per-file `rg` scan across `.github`, docs, active code, tests | high | Distinguished live CI/operator scripts from disconnected one-offs. |
| `invoke_cloud_timer.cmd` runtime relevance | 2026-03-21 | Codex | no active refs, plus file still launches removed flat `agent\\invoke_function_smoke.py` | high | Safe archive candidate rather than active script. |

## Changes
- Archived disconnected `scripts/invoke_cloud_timer.cmd` under `archive/work/scripts/`.
- Refreshed `scripts/check_no_legacy_imports.py` to scan the current active contour (`index.py`, `local_run.py`, `src/contexts`, `src/entrypoints`, `src/platform`) instead of removed technical roots.
- Refreshed `scripts/check_no_monsters.py` so its remaining regression scope follows the current platform/entrypoint map.

## Verification
- `rg -n --fixed-strings "invoke_cloud_timer.cmd" .`
- `python scripts/check_no_monsters.py`
- `python scripts/check_no_legacy_imports.py`
- `python scripts/check_no_legacy_entrypoint_imports.py`

## Outcome
- `scripts/` now contains only live CI guardrails and active observability tooling.
- The disconnected cloud-timer wrapper survives only as historical operator context in archive.
- Workflow guard scripts now describe the current repo shape instead of long-removed roots.
