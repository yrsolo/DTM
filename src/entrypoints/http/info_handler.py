"""Operational info dashboard handler."""

from __future__ import annotations

import json
from datetime import timezone
from html import escape
from typing import Any

from src.app.context import AppContext
from src.entrypoints.http.dto import HttpRequest, HttpResponse
from src.entrypoints.http.event_parser import normalize_path
from src.entrypoints.http.response_utils import html_response, json_response
from src.snapshot_engine.engine import build_snapshot_engine


def _human_size(value: int) -> str:
    size = float(max(0, int(value)))
    units = ["B", "KB", "MB", "GB", "TB"]
    idx = 0
    while size >= 1024 and idx < len(units) - 1:
        size /= 1024.0
        idx += 1
    return f"{size:.2f} {units[idx]}"


def _render_info_page(payload: dict[str, Any]) -> str:
    escaped = escape(json.dumps(payload, ensure_ascii=False))
    return f"""<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>DTM Info</title>
  <style>
    body{{font-family:Segoe UI,Arial,sans-serif;background:#f3f6fb;margin:0;padding:20px;color:#0d1b2a}}
    .grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:16px}}
    .card{{background:#fff;border-radius:12px;padding:16px;box-shadow:0 2px 10px rgba(0,0,0,.06)}}
    h1{{margin:0 0 16px}} h2{{margin:0 0 12px;font-size:18px}}
    .k{{font-weight:600}} .v{{font-family:Consolas,monospace}}
    .row{{margin:6px 0}}
    .controls{{display:flex;flex-wrap:wrap;gap:10px;align-items:center;margin:8px 0}}
    .controls label{{display:flex;align-items:center;gap:6px}}
    .section{{margin-top:16px}}
    .hline{{display:flex;align-items:center;justify-content:space-between;gap:10px}}
    .timer{{font-family:Consolas,monospace;font-size:14px;color:#475569}}
    input[type="number"],input[type="date"]{{padding:6px 8px;border:1px solid #cbd5e1;border-radius:8px}}
    button{{margin:4px 6px 4px 0;padding:8px 10px;border:0;border-radius:8px;background:#0f62fe;color:#fff;cursor:pointer}}
    button.alt{{background:#4b5563}}
    button.small{{padding:6px 8px;font-size:12px}}
    pre{{background:#0b1220;color:#dbeafe;padding:12px;border-radius:10px;overflow:auto;max-height:280px;white-space:pre-wrap}}
  </style>
</head>
<body>
  <h1>DTM Info Dashboard</h1>
  <div class="grid">
    <div class="card">
      <h2>Snapshot Meta</h2>
      <div class="row"><span class="k">Env:</span> <span class="v" id="env"></span></div>
      <div class="row"><span class="k">Bucket:</span> <span class="v" id="bucket"></span></div>
      <div class="row"><span class="k">SourceId:</span> <span class="v" id="sourceId"></span></div>
      <div class="row"><span class="k">SourceHash:</span> <span class="v" id="sourceHash"></span></div>
      <div class="row"><span class="k">Raw fetched:</span> <span class="v" id="rawFetchedAt"></span></div>
      <div class="row"><span class="k">Prep built:</span> <span class="v" id="prepBuiltAt"></span></div>
    </div>
    <div class="card">
      <h2>Records</h2>
      <div class="row"><span class="k">Total tasks:</span> <span class="v" id="tasksTotal"></span></div>
      <div class="row"><span class="k">By status:</span> <span class="v" id="statusCounts"></span></div>
    </div>
    <div class="card">
      <h2>Storage</h2>
      <div class="row"><span class="k">Objects:</span> <span class="v" id="objectsTotal"></span></div>
      <div class="row"><span class="k">Size bytes:</span> <span class="v" id="bytesTotal"></span></div>
      <div class="row"><span class="k">Size human:</span> <span class="v" id="bytesHuman"></span></div>
      <div class="row"><span class="k">Breakdown:</span> <span class="v" id="sizeBreakdown"></span></div>
    </div>
  </div>

  <div class="card section">
    <div class="hline">
      <h2>Admin Actions</h2>
      <span class="timer" id="adminTimer">00:00.0</span>
    </div>
    <button onclick="runMode({{mode:'sync-only',force_refresh:true}})">Force snapshot refresh</button>
    <button onclick="runMode({{mode:'timer',force_refresh:true}})">Force render table</button>
    <button onclick="runMode({{mode:'test',mock_external:false,dry_run:false}})">Notify test chat</button>
    <button onclick="runMode({{mode:'morning',mock_external:false,dry_run:false}})">Notify designer chats</button>
    <pre id="adminResult">Готово к запуску действий.</pre>
  </div>

  <div class="card section">
    <div class="hline">
      <h2>API Request Builder</h2>
      <span class="timer" id="apiTimer">00:00.0</span>
    </div>
    <div class="controls">
      <label><input id="includePeople" type="checkbox" checked /> include_people</label>
    </div>
    <div class="controls">
      <label>limit <input id="limitValue" type="number" min="1" max="2000" value="200" /></label>
      <button class="alt small" onclick="setLimit(20)">20</button>
      <button class="alt small" onclick="setLimit(100)">100</button>
      <button class="alt small" onclick="setLimit(200)">200</button>
      <button class="alt small" onclick="setLimit(500)">500</button>
    </div>
    <div class="controls">
      <span class="k">statuses:</span>
      <label><input id="stWork" type="checkbox" checked /> work</label>
      <label><input id="stPreDone" type="checkbox" checked /> pre_done</label>
      <label><input id="stWait" type="checkbox" /> wait</label>
      <label><input id="stDone" type="checkbox" /> done</label>
    </div>
    <div class="controls">
      <label>window start <input id="windowStart" type="date" /></label>
      <label>window end <input id="windowEnd" type="date" /></label>
      <button class="alt small" onclick="setWindowPreset(7)">next 7d</button>
      <button class="alt small" onclick="setWindowPreset(14)">next 14d</button>
      <button class="alt small" onclick="clearWindow()">clear window</button>
    </div>
    <div class="controls">
      <button onclick="sendApiBuilder()">Send</button>
      <button class="alt" onclick="applyApiPreset('active20')">Preset: Active 20</button>
      <button class="alt" onclick="applyApiPreset('done20')">Preset: Done 20</button>
      <button class="alt" onclick="applyApiPreset('all100')">Preset: All 100</button>
      <button class="alt" onclick="applyApiPreset('window14')">Preset: Window 14d</button>
    </div>
    <div class="row"><span class="k">Request URL:</span></div>
    <pre id="apiRequestUrl"></pre>
    <pre id="apiResult">Соберите параметры и нажмите Send.</pre>
  </div>

  <div class="card section">
    <h2>Info JSON</h2>
    <pre id="infoResult">{escaped}</pre>
  </div>

  <script>
    function pretty(value){{
      if (typeof value === 'string') {{
        try {{
          return JSON.stringify(JSON.parse(value), null, 2);
        }} catch (_e) {{
          return value;
        }}
      }}
      return JSON.stringify(value, null, 2);
    }}
    function createTimer(elementId){{
      const el = document.getElementById(elementId);
      let startAt = 0;
      let intervalId = null;
      function format(ms){{
        const totalSec = ms / 1000.0;
        const mm = Math.floor(totalSec / 60);
        const ss = totalSec - mm * 60;
        const mmStr = String(mm).padStart(2, '0');
        const ssStr = ss.toFixed(1).padStart(4, '0');
        return mmStr + ':' + ssStr;
      }}
      return {{
        start(){{
          startAt = Date.now();
          if (intervalId) clearInterval(intervalId);
          el.textContent = '00:00.0';
          intervalId = setInterval(() => {{
            el.textContent = format(Date.now() - startAt);
          }}, 100);
        }},
        stop(){{
          if (intervalId) clearInterval(intervalId);
          intervalId = null;
          el.textContent = format(Date.now() - startAt);
        }},
      }};
    }}
    const adminTimer = createTimer('adminTimer');
    const apiTimer = createTimer('apiTimer');
    async function loadInfo(){{
      const r = await fetch('/info?format=json', {{cache:'no-store'}});
      const text = await r.text();
      let p = {{}};
      try {{
        p = JSON.parse(text);
      }} catch (_e) {{
        document.getElementById('infoResult').textContent = 'HTTP ' + r.status + '\\n' + text;
        return;
      }}
      const s = p.snapshot || {{}};
      const c = p.counts || {{}};
      const st = p.storage || {{}};
      document.getElementById('env').textContent = s.env || '';
      document.getElementById('bucket').textContent = s.bucket || '';
      document.getElementById('sourceId').textContent = s.sourceId || '';
      document.getElementById('sourceHash').textContent = s.sourceHash || '';
      document.getElementById('rawFetchedAt').textContent = s.rawFetchedAt || '';
      document.getElementById('prepBuiltAt').textContent = s.prepBuiltAt || '';
      document.getElementById('tasksTotal').textContent = c.tasksTotal ?? 0;
      document.getElementById('statusCounts').textContent = JSON.stringify(c.byStatus || {{}});
      document.getElementById('objectsTotal').textContent = st.objectsTotal ?? 0;
      document.getElementById('bytesTotal').textContent = st.bytesTotal ?? 0;
      document.getElementById('bytesHuman').textContent = st.bytesHuman || '';
      document.getElementById('sizeBreakdown').textContent = JSON.stringify(st.byPrefix || {{}});
      document.getElementById('infoResult').textContent = pretty(p);
    }}
    async function runMode(payload){{
      adminTimer.start();
      const r = await fetch('/', {{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify(payload)}});
      const t = await r.text();
      document.getElementById('adminResult').textContent = 'HTTP '+r.status+'\\n'+pretty(t);
      adminTimer.stop();
      setTimeout(loadInfo, 1500);
    }}
    function setIncludePeople(flag){{
      document.getElementById('includePeople').checked = !!flag;
    }}
    function setLimit(value){{
      document.getElementById('limitValue').value = String(value);
    }}
    function setWindowPreset(days){{
      const now = new Date();
      const end = new Date(now.getTime() + days * 24 * 60 * 60 * 1000);
      const toIso = (d) => d.toISOString().slice(0,10);
      document.getElementById('windowStart').value = toIso(now);
      document.getElementById('windowEnd').value = toIso(end);
    }}
    function clearWindow(){{
      document.getElementById('windowStart').value = '';
      document.getElementById('windowEnd').value = '';
    }}
    function selectedStatuses(){{
      const statuses = [];
      if (document.getElementById('stWork').checked) statuses.push('work');
      if (document.getElementById('stPreDone').checked) statuses.push('pre_done');
      if (document.getElementById('stWait').checked) statuses.push('wait');
      if (document.getElementById('stDone').checked) statuses.push('done');
      return statuses;
    }}
    function buildApiQuery(){{
      const statuses = selectedStatuses();
      const limit = document.getElementById('limitValue').value || '200';
      const includePeople = document.getElementById('includePeople').checked;
      const windowStart = document.getElementById('windowStart').value;
      const windowEnd = document.getElementById('windowEnd').value;
      const q = new URLSearchParams();
      if (statuses.length > 0) q.set('statuses', statuses.join(','));
      q.set('limit', String(limit));
      q.set('include_people', String(includePeople));
      if (windowStart && windowEnd) {{
        q.set('window_start', windowStart);
        q.set('window_end', windowEnd);
      }}
      return q;
    }}
    function refreshApiRequestUrl(){{
      const q = buildApiQuery();
      const origin = window.location.origin || '';
      document.getElementById('apiRequestUrl').textContent = origin + '/api/v2/frontend?' + q.toString();
    }}
    async function sendApiBuilder(){{
      apiTimer.start();
      const q = buildApiQuery();
      const r = await fetch('/api/v2/frontend?'+q.toString(), {{cache:'no-store'}});
      const t = await r.text();
      document.getElementById('apiResult').textContent = 'HTTP '+r.status+'\\n'+pretty(t);
      apiTimer.stop();
      refreshApiRequestUrl();
    }}
    function applyApiPreset(name){{
      if (name === 'active20') {{
        setIncludePeople(true);
        setLimit(20);
        document.getElementById('stWork').checked = true;
        document.getElementById('stPreDone').checked = true;
        document.getElementById('stWait').checked = false;
        document.getElementById('stDone').checked = false;
        clearWindow();
      }} else if (name === 'done20') {{
        setIncludePeople(false);
        setLimit(20);
        document.getElementById('stWork').checked = false;
        document.getElementById('stPreDone').checked = false;
        document.getElementById('stWait').checked = false;
        document.getElementById('stDone').checked = true;
        clearWindow();
      }} else if (name === 'all100') {{
        setIncludePeople(false);
        setLimit(100);
        document.getElementById('stWork').checked = true;
        document.getElementById('stPreDone').checked = true;
        document.getElementById('stWait').checked = true;
        document.getElementById('stDone').checked = true;
        clearWindow();
      }} else if (name === 'window14') {{
        setIncludePeople(true);
        setLimit(200);
        document.getElementById('stWork').checked = true;
        document.getElementById('stPreDone').checked = true;
        document.getElementById('stWait').checked = true;
        document.getElementById('stDone').checked = false;
        setWindowPreset(14);
      }}
      refreshApiRequestUrl();
    }}
    const watchIds = ['includePeople','limitValue','stWork','stPreDone','stWait','stDone','windowStart','windowEnd'];
    for (const id of watchIds) {{
      const el = document.getElementById(id);
      if (el) el.addEventListener('change', refreshApiRequestUrl);
      if (el && el.tagName === 'INPUT' && el.type === 'number') {{
        el.addEventListener('input', refreshApiRequestUrl);
      }}
    }}
    refreshApiRequestUrl();
    loadInfo();
  </script>
</body>
</html>"""


class InfoHandler:
    def __init__(self, ctx: AppContext) -> None:
        self._ctx = ctx

    def _storage_stats(self, bucket: str, root_prefix: str) -> dict[str, Any]:
        try:
            import boto3  # type: ignore
        except Exception:
            return {
                "objectsTotal": 0,
                "bytesTotal": 0,
                "bytesHuman": "n/a",
                "byPrefix": {},
                "error": "boto3_missing",
            }
        endpoint = str(self._ctx.cfg.db.object_storage.get("endpoint_url_default", "")).strip() or None
        client = boto3.client(
            "s3",
            endpoint_url=endpoint,
            aws_access_key_id=self._ctx.deps.get("aws_access_key_id"),
            aws_secret_access_key=self._ctx.deps.get("aws_secret_access_key"),
        )
        total_objects = 0
        total_bytes = 0
        by_prefix = {"raw": 0, "prep": 0, "extra": 0}
        token = None
        while True:
            kwargs = {"Bucket": bucket, "Prefix": root_prefix, "MaxKeys": 1000}
            if token:
                kwargs["ContinuationToken"] = token
            response = client.list_objects_v2(**kwargs)
            for item in response.get("Contents", []) or []:
                key = str(item.get("Key", ""))
                size = int(item.get("Size", 0))
                total_objects += 1
                total_bytes += size
                if "/raw/" in key:
                    by_prefix["raw"] += size
                elif "/prep/" in key:
                    by_prefix["prep"] += size
                elif "/extra/" in key:
                    by_prefix["extra"] += size
            if not response.get("IsTruncated"):
                break
            token = response.get("NextContinuationToken")
        return {
            "objectsTotal": total_objects,
            "bytesTotal": total_bytes,
            "bytesHuman": _human_size(total_bytes),
            "byPrefix": by_prefix,
        }

    def _resolve_root_prefix(self, raw_key: str) -> str:
        parts = [part for part in str(raw_key).split("/") if part]
        if len(parts) >= 2:
            return "/".join(parts[:2]) + "/"
        if parts:
            return parts[0] + "/"
        return ""

    def _info_payload(self) -> dict[str, Any]:
        prep = None
        raw = None
        snapshot_error = ""
        try:
            engine = build_snapshot_engine(self._ctx)
            prep = engine._prep_cache.get()  # noqa: SLF001
            raw = engine._raw_cache.get()  # noqa: SLF001
        except Exception as exc:  # pragma: no cover - safety for optional deps/runtime config
            snapshot_error = str(exc)
        status_counts: dict[str, int] = {}
        if prep is not None:
            for view in prep.tasks_by_id.values():
                key = str(view.sheet.status or "unknown")
                status_counts[key] = status_counts.get(key, 0) + 1

        env_name = str(self._ctx.cfg.runtime.runtime.env_default).strip().lower() or "dev"
        snap_cfg = self._ctx.cfg.runtime.snapshot_engine
        raw_key = str(snap_cfg.prefix_raw).replace("{env}", env_name)
        root_prefix = self._resolve_root_prefix(raw_key)
        storage = self._storage_stats(str(snap_cfg.bucket), root_prefix)
        return {
            "artifact": "dtm_info_dashboard",
            "snapshot": {
                "env": env_name,
                "error": snapshot_error,
                "bucket": str(snap_cfg.bucket),
                "rootPrefix": root_prefix,
                "rawKey": raw_key,
                "prepKey": str(snap_cfg.prefix_prep).replace("{env}", env_name),
                "extraPrefix": str(snap_cfg.prefix_extra).replace("{env}", env_name),
                "sourceId": "" if prep is None else str(prep.source_id),
                "sourceHash": "" if prep is None else str(prep.raw_source_hash),
                "rawFetchedAt": "" if raw is None else raw.fetched_at_utc.astimezone(timezone.utc).isoformat(),
                "prepBuiltAt": "" if prep is None else prep.built_at_utc.astimezone(timezone.utc).isoformat(),
            },
            "counts": {
                "tasksTotal": 0 if prep is None else len(prep.tasks_by_id),
                "byStatus": status_counts,
            },
            "storage": storage,
        }

    def handle(self, req: HttpRequest) -> HttpResponse | None:
        if not req.is_http_event:
            return None
        method = str(req.method or "GET").strip().upper()
        if method == "ANY":
            method = "GET"
        if method != "GET":
            return None
        path = normalize_path(req.path)
        if path not in {"/info", "/api/v2/info"}:
            return None
        payload = self._info_payload()
        as_json = str(req.query.get("format", "")).strip().lower() == "json" or path == "/api/v2/info"
        if as_json:
            return json_response(200, payload)
        return html_response(200, _render_info_page(payload))
