# CAM-2026-03-21-MODULE-POLISH-V1 Plan

Smell:
- active module surfaces still speak too much in builder-style assembly language even when they already act as canonical module APIs

Target ideal:
- active modules read like finished ownership centers, with method names that describe capabilities, handlers, requests, and jobs rather than generic construction steps

Kill criteria:
- active module methods no longer foreground `build_*` wording where the role is already stable and canonical
- the broad dead alias `get_snapshot_engine()` no longer appears in the active snapshot public surface
- active public facades and the closest runtime/tests keep working without behavior changes

Scope boundary:
- active context module/public surfaces only
- small supporting call-site rewrites where names change
- no payload or boundary redesign

Non-goals:
- no new module extraction work
- no runtime contract changes
- no test-layout changes
