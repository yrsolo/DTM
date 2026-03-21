# Work Artifacts

`work/artifacts/` stores generated local evidence and operator output files.

This is not application source code and not long-term archive.

## Typical contents

- `baseline/` - captured baseline bundles for local validation flows
- `tmp/` - transient smoke outputs and local JSON reports
- `shadow_run_stage8/` - generated evidence packs from historical/local artifact flows

## Rules

- generated files may be deleted and recreated
- do not place reusable Python modules here
- if output becomes historical record rather than active local working data, move it under `archive/work/`
