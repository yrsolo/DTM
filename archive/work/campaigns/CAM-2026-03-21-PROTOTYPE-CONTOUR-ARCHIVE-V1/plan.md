# CAM-2026-03-21-PROTOTYPE-CONTOUR-ARCHIVE-V1

## Goal

Archive the old prototype contour if it is disconnected from live runtime and deploy scenarios.

## Scope

- `web_prototype/`
- `agent/prototype/`
- stage8 prototype-evidence helpers in `agent/artifacts/`
- active docs/tracking references to this contour

## Non-goals

- no change to live `/info` or production browser surfaces
- no change to still-live artifact/contract smokes used by deploy workflows

## Tasks

- [x] verify live usage against runtime, deploy, and operator paths
- [x] move retired prototype files under `archive/work/`
- [x] remove active references and stale root docs
- [x] run targeted checks and close tracking

## Done when

- no active runtime/deploy path depends on the prototype contour
- `web_prototype/` and `agent/prototype/` are gone from the active repo surface
- stage8 prototype-evidence helpers live only in archive
