# Security Policy

## Reporting
If you find a vulnerability or secret exposure, report privately to repository owner first.  
Do not open a public issue with secret details.

## Secret Handling Rules
- Keep all secrets in `.env` or secret manager.
- Never commit:
  - API tokens
  - service account key contents
  - proxy credentials
  - personal sensitive data
- Rotate leaked credentials immediately.

## Pre-Publish Checklist
1. Run secret scan on tracked files.
2. Verify `.env` and key files are ignored.
3. Check notebooks/output for accidental token dumps.
4. Review `old/` and `doc/` for hardcoded credentials.

## Scope Notes
- Historical snapshots in `old/` are useful for migration, but must remain secret-clean.
- Public repo must contain only placeholders in examples.

