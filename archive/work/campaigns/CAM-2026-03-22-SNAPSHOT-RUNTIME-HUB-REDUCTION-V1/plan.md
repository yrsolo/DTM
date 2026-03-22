# CAM-2026-03-22-SNAPSHOT-RUNTIME-HUB-REDUCTION-V1

## Smell
- `snapshot` still hides too much coordination gravity inside one broad runtime bundle, so the module reads as a capability facade over an internal hub instead of a calm set of role-true services

## Target ideal
- `snapshot` application APIs depend on direct role-true services and stores
- shared runtime builders stay small and specific
- no broad `runtime binding of everything` is needed to understand the active module surface

## Kill criteria
- `SnapshotReadApi`, `SnapshotQueryApi`, `SnapshotAttachmentApi`, and `SnapshotUpdateApi` no longer depend on one broad runtime bundle
- `snapshot/module.py` composes APIs from smaller builders with clearer ownership
- update/query/attachment paths and their active tests remain unchanged

## Out of scope
- deleting the legacy `SnapshotEngine` facade entirely
- changing payload contracts or storage keys
- changing `access_api` route behavior
