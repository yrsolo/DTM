# Anti-Fake Modularity Rules

The following do not count as architectural progress by themselves:
- a new adapter
- a new connector interface
- a new wrapper
- a new facade
- a new shell
- a new dispatcher layer

They count only if all are true:
- ownership moved to the intended module
- the path to read the scenario became shorter or clearer
- the old path died, was demoted, or was explicitly deprecated
- the read/write/publication model became clearer

## Smells to reject

- facade over a historical cluster that remains the real implementation center
- lazy getter chains without ownership benefit
- router -> dispatcher -> shell -> bridge -> handler ladders
- transport files that still hide business ownership
- "temporary" compatibility paths with no removal task
