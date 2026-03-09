# Configuration (Current)

## Source of truth
Typed config is loaded through:
- `src/config/schema.py`
- `src/config/loader.py`
- composed in `src/app/bootstrap.py`

Primary config files:
- `config/runtime.yaml`
- `config/tables.yaml`
- `config/db.yaml`
- `config/llm.yaml`
- `config/mapping.yaml`
- `config/deploy.yaml`

## Runtime contour
- `runtime.env`: `dev|test|prod`
- `runtime.timezone`: default `Europe/Moscow`
- `runtime.snapshot_engine.*`: snapshot/Object Storage settings
- `runtime.queue.*`: Yandex Message Queue settings
- `runtime.telegram.*`: webhook and sender settings
- `runtime.notify.*`: reminder retry/enhancer/test-chat policy

## Secrets
Secrets stay outside repo config files:
- Google credentials
- Object Storage credentials
- Telegram token
- LLM provider tokens
- Yandex Cloud auth/service secrets

They are resolved through secret storage / env in loader/bootstrap only.

## Object Storage
Used for:
- raw snapshot
- prep snapshot
- people snapshot
- extra metadata
- attachment binaries
- job status/history

## Queue
Queue config defines:
- enabled flag
- queue URLs for test/prod
- status/history prefixes
- endpoint/auth data for live queue introspection

## Deploy workflows
Current workflows:
- `.github/workflows/deploy_yc_function_main.yml` — deploy on push to `test`
- `.github/workflows/release_yc_function_prod.yml` — manual prod release

## Config policy
- no `os.getenv()` outside loader/bootstrap
- services receive typed config objects
- env-based branching belongs in bootstrap/policy selection, not inside core services
