# Target Folder Structure

## Top-level reading structure

```text
src/
  entrypoint/
  platform/
    runtime/
  contexts/
    snapshot/
    rendering/
    reminders/
    attachments/
    access_api/
    telegram_interaction/
```

## What the structure should teach

- start from `entrypoint`
- move into `platform.runtime`
- land in one owning module

The folder tree should not teach:
- that runtime glue is the system brain
- that technical helpers are the primary architecture
- that HTTP handlers or old compatibility zones are ownership centers

## Module shape

Each active module should read roughly as:

```text
contexts/<module>/
  public.py
  module.py
  contracts/
  internal/ or application/
  domain/
  adapters/
```

Exact subfolders may differ, but the public entry and builder must stay obvious.
