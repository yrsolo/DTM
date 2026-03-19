# Notes For Maintainers

## Ask the ownership question first

Do not ask:
- which handler should own this
- which services package should hold this
- which helper should this be tucked into

Ask:
- which owning module is responsible for this scenario

## Do not rebuild a mega-bootstrap

If a new scenario needs module assembly, it belongs in `src/contexts/<module>/module.py`, not in bootstrap.

## Do not glue modules with cache

New mutating flows must publish aftermath through intents, jobs, or runtime-owned invalidation orchestration.

## Do not hide routing behind magic

The top path and queue routing should stay obvious to the eye.

## Do not let old clusters become architecture centers again

Historical roots may survive only as temporary implementation zones or archive/reference zones.
They are not acceptable as the place where new development naturally accumulates.
