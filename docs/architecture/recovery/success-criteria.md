# Success Criteria

The program is successful only if all conditions are true at the same time.

## Entry

- top path fits in 1-2 screens
- mode routing is explicit
- command routing is explicit
- no hidden routing magic competes with the visible path

## Runtime

- `platform.runtime` is orchestration-only
- queue dispatch is ownership-based
- triggers are orchestration-only

## Bootstrap

- bootstrap is not the hidden brain of the system
- new domain-specific assembly does not accumulate there
- module-local builders are the norm

## Modules

- all six first-class modules exist as real ownership centers
- each one has an obvious public facade
- scenario ownership no longer has to be guessed

## Boundaries

- modules communicate through public surfaces, contracts, commands, queries, or intents
- cache is coordinated through intents/jobs rather than direct helper imports
- old technical clusters are no longer needed to understand active scenarios

## Readability

- a new engineer can open entrypoint, one module facade, and one module builder and understand the scenario in under a minute
