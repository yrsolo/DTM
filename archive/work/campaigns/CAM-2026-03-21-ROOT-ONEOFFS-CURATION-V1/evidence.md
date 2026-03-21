# CAM-2026-03-21-ROOT-ONEOFFS-CURATION-V1 Evidence

## Trust Gate

| source | last_verified_at | verified_by | evidence | trust_level | notes |
| --- | --- | --- | --- | --- | --- |
| root repo surface | 2026-03-21 | Codex | `Get-ChildItem -Force` at repo root | high | Verified current active root files and directories before the cut. |
| `run_alert_eval_ci.cmd` usage | 2026-03-21 | Codex | `rg -n --fixed-strings "run_alert_eval_ci.cmd" .` | high | Only historical archive references remained; no live runtime, CI, docs, or active operator usage. |
| `profile_runtime_path.py` usage | 2026-03-21 | Codex | `rg -n --fixed-strings "profile_runtime_path.py" .` | high | Only self-reference plus archived notebook copy remained. |
| `run_timer.cmd` usage | 2026-03-21 | Codex | `rg -n --fixed-strings "run_timer.cmd" .` | high | Still referenced by deploy workflows; explicitly excluded from archive cut. |

## Changes
- Archived disconnected root command `run_alert_eval_ci.cmd` under `archive/work/root_commands/`.
- Removed duplicate root `profile_runtime_path.py`.
- Removed root `__pycache__/`.

## Verification
- `rg -n --fixed-strings "run_alert_eval_ci.cmd" .`
- `rg -n --fixed-strings "profile_runtime_path.py" .`
- `rg -n --fixed-strings "run_timer.cmd" .`
- `python -m unittest tests.architecture.test_guardrails_v0 tests.entrypoints.test_import_safety tests.platform.test_bootstrap_inputs -v`
- `if (Test-Path -LiteralPath '.\\__pycache__') { 'ROOT_PYCACHE_ACTIVE' } else { 'ROOT_PYCACHE_REMOVED' }`

## Outcome
- Root one-off clutter was reduced without touching live runtime or CI surfaces.
- `run_alert_eval_ci.cmd` was archived as a disconnected historical wrapper.
- `profile_runtime_path.py` now survives only in archive notebooks.
- `run_timer.cmd` remained active because deploy workflows still call it.
