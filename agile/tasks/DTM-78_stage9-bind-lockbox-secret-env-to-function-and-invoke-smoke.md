# DTM-78: TSK-081 Stage 9 bind Lockbox secret env to function and run invoke smoke

## Context
- Lockbox secret `DTM` is populated from local contour.
- Stage 9 requires runtime binding of Lockbox entries to Cloud Function env and verified invoke path.

## Goal
- Grant runtime function service account access to Lockbox payload.
- Create a new function version with Lockbox `secret` mappings for all payload keys.
- Run cloud invoke smoke.

## Non-goals
- No runtime behavior refactor in this task.
- No frontend prototype feature changes.

## Plan
1. Resolve function/runtime SA and secret metadata.
2. Ensure `lockbox.payloadViewer` binding for runtime SA.
3. Publish new function version with secret-to-env mappings.
4. Run invoke smoke and record result.

## Checklist (DoD)
- [x] Runtime SA has Lockbox payload read role.
- [x] New function version created with Lockbox secret mappings.
- [x] Invoke smoke executed.
- [x] Sprint/context/Jira synchronized.

## Work log
- 2026-02-27: DTM-78 created and moved to `V rabote`.
- 2026-02-27: Added Lockbox access binding for runtime SA `aje1kqd422vq2vefkbbl`.
- 2026-02-27: Created new function version `d4epk6q33gfq33marsom` with 29 secret env mappings from Lockbox `DTM` version `e6qj37dvpcd4tm7kbcf1`.
- 2026-02-27: Invoke smoke executed (`yc serverless function invoke --name dtm ...`) returned HTTP 200 payload `{\"statusCode\": 200, \"body\": \"Hello World!\"}`; follow-up needed to deploy repository runtime package to function.

## Links
- Jira: DTM-78
