# Migration Rules

## Rule 1: No parallel canon

This architecture-recovery set is historical precedent.
Use `docs/architecture/module-first-recovery/` as the active normative source.
Current runtime docs remain descriptive evidence only.

## Rule 2: Every wave must improve ownership

A wave is valid only if it:
- shortens the path to the owning module
- reduces competing bridges or delegators
- makes the system easier to read top-down

## Rule 3: Every wave must kill something old

Each implementation wave must remove, ban, or hard-deprecate at least one old path.
New wrappers without old-path removal do not count as architectural progress.

## Rule 4: Bootstrap may only delegate

`src/app/bootstrap.py` may assemble runtime glue but must not absorb new domain-specific wiring.

## Rule 5: Guardrails are part of the change

If a wave introduces a new ownership rule, it must also add a test or guardrail so the old style cannot quietly grow back.

## Rule 6: Beauty follows ownership

Do not start with mass file moves for cosmetic path cleanup.
Ownership must move first; file geography may then be aligned to reflect the new truth.
