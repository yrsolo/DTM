# CAM-2026-03-22-BOOTSTRAP-SHELL-EXTRACTION-V1

## Smell
- `src/platform/bootstrap.py` is still too visible as a top-entry catalog because it owns lazy shell singletons, webhook path lookup, and trigger-mode lookup in addition to context/dependency assembly

## Target ideal
- `bootstrap` stays a boring platform composition root for config/env/dependency assembly
- top-entry shell/webhook/trigger seams live in `src/platform/shell`
- `index.py` and top-path readers no longer treat `bootstrap` as the main semantic home for runtime dispatch

## Kill criteria
- `get_http_shell`, `get_worker_shell`, `get_trigger_shell`, `get_runtime_shell`, `get_telegram_webhook_path`, and `get_trigger_modes` move out of `src/platform/bootstrap.py`
- `index.py` imports top-entry seams from `src/platform/shell`
- existing top-path behavior and tests remain unchanged

## Out of scope
- deeper `snapshot` interior redesign
- `get_app_context` / `get_runtime_deps` removal
- env/config loader changes
