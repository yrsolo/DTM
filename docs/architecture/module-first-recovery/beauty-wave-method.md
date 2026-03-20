# Beauty Wave Method

Use this method when executing the beauty backlog from [repo-beauty-audit-2026-03-21.md](repo-beauty-audit-2026-03-21.md).

This is a curation workflow, not another architecture-recovery program.

## Core Principle

- each wave must kill one visible smell
- a wave is successful only when that smell disappears
- the repo should look noticeably cleaner after each wave, not just score better on paper

## Wave Order

Execute beauty waves in this order unless a later wave is explicitly re-prioritized for a concrete reason:

1. `Top-path elegance`
2. `Active naming cleanup`
3. `Docs voice unification`
4. `Bootstrap readability`
5. `Active/history separation`
6. `Module polish`
7. `Showcase polish`

This order is based on visual and reader-facing impact, not runtime importance.

## Wave Format

Every beauty wave must define:

- `smell`: one concrete kind of ugliness or awkwardness
- `target ideal`: what the active contour should look like after the wave
- `kill criteria`: the exact pass/fail condition that means the smell is gone
- `scope boundary`: what files or areas are in scope
- `non-goals`: what this wave explicitly does not change

Do not mix multiple smell categories in one wave.

## Status Discipline

Every issue touched by beauty work must be labeled as one of:

- `required`
- `nice to have`
- `accepted imperfection`

Use these labels in audit updates, campaign plans, and closeout notes so polish does not grow without a stop condition.

## Good Wave Size

Beauty waves should stay small and easy to reason about:

- 1-2 days of work
- usually 3-10 files, sometimes up to 15
- one smell only
- easy to explain in one paragraph
- easy to revert if needed

If a wave starts mixing naming, docs voice, bootstrap, and module cleanup at the same time, split it.

## Execution Rhythm

For every wave:

1. Open one small campaign.
2. Record trust sources and verify the active contour against code.
3. Freeze smell, target ideal, kill criteria, scope boundary, and non-goals before editing.
4. Change only what serves that smell.
5. Run a short smoke or grep-based verification appropriate to the wave.
6. Close with a short verdict:
   - what looked ugly before
   - what disappeared
   - what is now the next worst visible smell
7. Update the beauty audit with one short progress note, not a new full audit.

## Wave Closeout Format

Use this closeout shape after each beauty wave:

- `before`: what specifically looked unfinished or awkward
- `after`: what specifically disappeared
- `next worst thing`: what should be tackled next and why

Do not write another broad architecture essay at wave closeout.

## First Wave

The first beauty wave is always `Top-path elegance`.

Its default smell is:
- residual ceremony in `index.py` and the closest entrypoint contour

Its default kill criteria are:
- no top-path context lookup remains in the top path
- no stale glue helpers remain in `index.py`
- `index.py -> src/entrypoint/handler.py -> one shell` reads without explanation

## What Not To Do

- do not open a new umbrella reform program
- do not reinterpret the architecture canon after every wave
- do not add new audit documents instead of removing a concrete smell
- do not mix beauty work with unrelated runtime redesign
- do not polish issues that do not affect readability, ownership understanding, or finished-system feel

## Stop Condition

Beauty work should stop when the beauty audit stop rule is satisfied and all remaining issues are either:

- `nice to have`, or
- explicitly accepted imperfections
