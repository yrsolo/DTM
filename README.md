## Sponsor Table

### Local run

Direct mode run:

```bash
python local_run.py --mode test
python local_run.py --mode timer
python local_run.py --mode morning
```

Event emulation (as in Yandex trigger):

```bash
python local_run.py --trigger-id a1sldapc8v2pha7dichv
python local_run.py --trigger-id a1smsif4rc82qbj1e3hf
python local_run.py --event-file ./event.json
```

Notebook run is still supported:

```python
from main import main
import asyncio

await main(mode="test")
# or
await main(event="morning")
```

### Snapshot storage (Yandex Object Storage / S3)

Env vars are supported via `.env`:
- `S3_ENDPOINT_URL`
- `S3_BUCKET`
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`

Example usage:

```python
from utils.storage import S3SnapshotStorage

storage = S3SnapshotStorage()
storage.upload_json("snapshots/sample.json", {"ok": True})
```
