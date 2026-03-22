# Top-Path Readability

## Rule

A scenario should usually be understandable in about 3 to 4 jumps:

- entrypoint
- runtime routing
- module public surface
- module-local builder or use case

## Anti-regression rule

`index.py` and entrypoint code may stay thin, but they must not grow empty delegating chains.

The following count as readability regressions unless they provide clear ownership value:
- lazy getter chains
- wrapper-over-wrapper delegation
- shell around bridge around handler
- new runtime indirection without path shortening

## Audit expectation

Every delta audit should explicitly note:
- whether the top path is still readable
- where empty delegation or chain growth has returned
- which next kill move would shorten the path
