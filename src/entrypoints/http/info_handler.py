"""Operational info dashboard handler."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from html import escape
from typing import Any

from src.app.context import AppContext
from src.entrypoints.http.dto import HttpRequest, HttpResponse
from src.entrypoints.http.event_parser import normalize_path
from src.entrypoints.http.response_utils import html_response, json_response
from src.infra.yc_function_info import get_function_build_info
from src.infra.yc_queue_info import get_queue_live_stats
from src.snapshot_engine.engine import build_snapshot_engine
from src.worker.model import JobStatusRecord


def _human_size(value: int) -> str:
    size = float(max(0, int(value)))
    units = ["B", "KB", "MB", "GB", "TB"]
    idx = 0
    while size >= 1024 and idx < len(units) - 1:
        size /= 1024.0
        idx += 1
    return f"{size:.2f} {units[idx]}"


def _iso(value: datetime | None) -> str:
    if value is None:
        return ""
    return value.astimezone(timezone.utc).isoformat()


def _job_record_payload(record: JobStatusRecord) -> dict[str, Any]:
    return {
        "jobId": record.job_id,
        "commandType": record.command_type,
        "status": record.status,
        "requestedAt": _iso(record.requested_at_utc),
        "startedAt": _iso(record.started_at_utc),
        "finishedAt": _iso(record.finished_at_utc),
        "requestedBy": dict(record.requested_by),
        "summary": dict(record.summary),
        "warnings": list(record.warnings),
        "retryable": bool(record.retryable),
        "error": dict(record.error or {}) if record.error else None,
    }


def _render_debug_payload(record: JobStatusRecord | None) -> dict[str, Any]:
    if record is None:
        return {
            "lastJobId": "",
            "state": "unknown",
            "reason": "no_render_job_history",
            "details": {},
        }
    summary = dict(record.summary or {})
    warnings = [str(item) for item in list(record.warnings or [])]
    error = dict(record.error or {}) if record.error else {}
    if record.status in {"failed_terminal", "failed_retryable"}:
        if str(error.get("code", "")).strip() == "render_target_unsafe":
            state = "blocked"
            reason = "blocked_by_target_safety_guard"
        else:
            state = "failed"
            reason = str(error.get("code", "")).strip() or "render_job_failed"
    elif record.status == "success":
        if bool(summary.get("render_applied", False)):
            state = "applied"
            reason = "render_applied_successfully"
        else:
            state = "noop"
            reason = warnings[0] if warnings else "render_not_applied"
    elif record.status in {"accepted", "running"}:
        state = "pending"
        reason = f"job_{record.status}"
    else:
        state = "unknown"
        reason = record.status or "unknown"
    return {
        "lastJobId": record.job_id,
        "state": state,
        "reason": reason,
        "details": _job_record_payload(record),
    }


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
    <div class="card">
      <h2>Function Build</h2>
      <div class="row"><span class="k">Function:</span> <span class="v" id="buildFunctionName"></span></div>
      <div class="row"><span class="k">Version:</span> <span class="v" id="buildVersionId"></span></div>
      <div class="row"><span class="k">Deployed:</span> <span class="v" id="buildDeployedAt"></span></div>
      <div class="row"><span class="k">Runtime:</span> <span class="v" id="buildRuntime"></span></div>
      <div class="row"><span class="k">Memory/timeout:</span> <span class="v" id="buildResources"></span></div>
      <div class="row"><span class="k">Entrypoint:</span> <span class="v" id="buildEntrypoint"></span></div>
    </div>
    <div class="card">
      <h2>Queue State</h2>
      <div class="row"><span class="k">Name:</span> <span class="v" id="queueName"></span></div>
      <div class="row"><span class="k">Visible:</span> <span class="v" id="queueVisible"></span></div>
      <div class="row"><span class="k">In flight:</span> <span class="v" id="queueInflight"></span></div>
      <div class="row"><span class="k">Delayed:</span> <span class="v" id="queueDelayed"></span></div>
      <div class="row"><span class="k">DLQ:</span> <span class="v" id="queueDlq"></span></div>
      <div class="row"><span class="k">Error:</span> <span class="v" id="queueError"></span></div>
    </div>
  </div>

  <div class="grid section">
    <div class="card">
      <h2>Recent Jobs</h2>
      <pre id="recentJobs">[]</pre>
    </div>
    <div class="card">
      <h2>Last Errors</h2>
      <pre id="recentErrors">[]</pre>
    </div>
    <div class="card">
      <h2>Last Render Job</h2>
      <pre id="lastRenderJob">{{}}</pre>
    </div>
    <div class="card">
      <h2>Render Debug</h2>
      <pre id="renderDebug">{{}}</pre>
    </div>
  </div>

  <div class="card section">
    <div class="hline">
      <h2>Admin Actions</h2>
      <span class="timer" id="adminTimer">00:00.0</span>
    </div>
    <button onclick="enqueueAdminCommand('/admin/commands/update-snapshot', {{force_refresh:true,dry_run:false}})">Force snapshot refresh</button>
    <button onclick="enqueueAdminCommand('/admin/commands/render-timeline', {{statuses:['work','pre_done'],dry_run:false}})">Force render table</button>
    <button onclick="enqueueAdminCommand('/admin/commands/send-reminders', {{mode:'test',statuses:['work','pre_done'],include_today:true,include_next_workday:true,force_test_chat:true,mock_external:false}})">Notify test chat</button>
    <button onclick="enqueueAdminCommand('/admin/commands/send-reminders', {{mode:'morning',statuses:['work','pre_done'],include_today:true,include_next_workday:true,force_test_chat:false,mock_external:false}})">Notify designer chats</button>
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
    function formatUtcAndMsk(value){{
      const text = String(value || '').trim();
      if (!text) return '';
      const date = new Date(text);
      if (Number.isNaN(date.getTime())) return text;
      const utc = date.toISOString();
      const msk = new Intl.DateTimeFormat('ru-RU', {{
        timeZone: 'Europe/Moscow',
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: false,
      }}).format(date);
      return utc + ' / MSK ' + msk;
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
      const q = p.queue || {{}};
      const ql = q.live || {{}};
      const b = p.build || {{}};
      const jobs = p.jobs || {{}};
      const recent = jobs.recent || [];
      const failed = jobs.failedRecent || [];
      const latestByCommand = jobs.latestByCommand || {{}};
      const lastRender = latestByCommand.render_timeline_sheet || null;
      const renderDebug = p.renderDebug || {{}};
      document.getElementById('env').textContent = s.env || '';
      document.getElementById('bucket').textContent = s.bucket || '';
      document.getElementById('sourceId').textContent = s.sourceId || '';
      document.getElementById('sourceHash').textContent = s.sourceHash || '';
      document.getElementById('rawFetchedAt').textContent = formatUtcAndMsk(s.rawFetchedAt);
      document.getElementById('prepBuiltAt').textContent = formatUtcAndMsk(s.prepBuiltAt);
      document.getElementById('tasksTotal').textContent = c.tasksTotal ?? 0;
      document.getElementById('statusCounts').textContent = JSON.stringify(c.byStatus || {{}});
      document.getElementById('objectsTotal').textContent = st.objectsTotal ?? 0;
      document.getElementById('bytesTotal').textContent = st.bytesTotal ?? 0;
      document.getElementById('bytesHuman').textContent = st.bytesHuman || '';
      document.getElementById('sizeBreakdown').textContent = JSON.stringify(st.byPrefix || {{}});
      document.getElementById('buildFunctionName').textContent = b.functionName || '';
      document.getElementById('buildVersionId').textContent = b.activeVersionId || '';
      document.getElementById('buildDeployedAt').textContent = b.error || formatUtcAndMsk(b.deployedAt);
      document.getElementById('buildRuntime').textContent = b.runtime || '';
      document.getElementById('buildResources').textContent = (b.memory || '') + ((b.timeoutSeconds ?? '') !== '' ? ' / ' + String(b.timeoutSeconds) + 's' : '');
      document.getElementById('buildEntrypoint').textContent = b.entrypoint || '';
      document.getElementById('queueName').textContent = ql.queue_name || q.queueName || '';
      document.getElementById('queueVisible').textContent = String(ql.messages_visible ?? '');
      document.getElementById('queueInflight').textContent = String(ql.messages_in_flight ?? '');
      document.getElementById('queueDelayed').textContent = String(ql.messages_delayed ?? '');
      document.getElementById('queueDlq').textContent = ql.dlq_configured === undefined ? '' : String(!!ql.dlq_configured);
      document.getElementById('queueError').textContent = ql.error || '';
      document.getElementById('recentJobs').textContent = pretty(recent);
      document.getElementById('recentErrors').textContent = pretty(failed);
      document.getElementById('lastRenderJob').textContent = pretty(lastRender || {{}});
      document.getElementById('renderDebug').textContent = pretty(renderDebug);
      document.getElementById('infoResult').textContent = pretty(p);
    }}
    async function pollJob(jobId){{
      for (let attempt = 0; attempt < 60; attempt += 1) {{
        const r = await fetch('/admin/jobs/' + encodeURIComponent(jobId), {{cache:'no-store'}});
        const text = await r.text();
        let payload = text;
        try {{
          payload = JSON.parse(text);
        }} catch (_e) {{}}
        document.getElementById('adminResult').textContent = 'HTTP ' + r.status + '\\n' + pretty(payload);
        if (r.ok && payload && typeof payload === 'object') {{
          const status = String(payload.status || '').toLowerCase();
          if (status === 'success' || status === 'failed_retryable' || status === 'failed_terminal') {{
            return;
          }}
        }}
        await new Promise((resolve) => setTimeout(resolve, 2000));
      }}
    }}
    async function enqueueAdminCommand(url, payload){{
      adminTimer.start();
      const r = await fetch(url, {{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify(payload)}});
      const t = await r.text();
      let parsed = t;
      try {{
        parsed = JSON.parse(t);
      }} catch (_e) {{}}
      document.getElementById('adminResult').textContent = 'HTTP '+r.status+'\\n'+pretty(parsed);
      if (r.ok && parsed && typeof parsed === 'object' && parsed.job_id) {{
        await pollJob(parsed.job_id);
      }}
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
        by_prefix = {"raw": 0, "prep": 0, "extra": 0, "attachments": 0, "jobs": 0}
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
                elif "/attachments/" in key:
                    by_prefix["attachments"] += size
                elif "/jobs/" in key:
                    by_prefix["jobs"] += size
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

    def _latest_jobs_payload(self, status_store: Any) -> dict[str, Any]:
        latest_jobs: dict[str, Any] = {}
        for command_type in (
            "update_snapshot",
            "send_reminders",
            "render_timeline_sheet",
            "render_designers_sheet",
            "group_query_reply",
            "attach_task_file",
        ):
            try:
                record = status_store.get_latest(command_type)
            except Exception:
                record = None
            if record is None:
                continue
            latest_jobs[command_type] = _job_record_payload(record)
        return latest_jobs

    def _recent_jobs_payload(self, status_store: Any) -> dict[str, Any]:
        try:
            recent_records = list(status_store.get_recent(20))
        except Exception as exc:
            return {"recent": [], "failedRecent": [], "error": str(exc)}
        recent_payload = [_job_record_payload(record) for record in recent_records]
        failed_payload = [
            item
            for item in recent_payload
            if str(item.get("status", "")).lower() in {"failed_retryable", "failed_terminal"}
        ]
        latest_by_command: dict[str, Any] = {}
        for item in recent_payload:
            command_type = str(item.get("commandType", "")).strip()
            if command_type and command_type not in latest_by_command:
                latest_by_command[command_type] = item
        last_successful_render = next(
            (
                item
                for item in recent_payload
                if str(item.get("commandType", "")) == "render_timeline_sheet"
                and str(item.get("status", "")).lower() == "success"
                and bool(dict(item.get("summary", {}) or {}).get("render_applied", False))
            ),
            None,
        )
        last_successful_update = next(
            (
                item
                for item in recent_payload
                if str(item.get("commandType", "")) == "update_snapshot"
                and str(item.get("status", "")).lower() == "success"
            ),
            None,
        )
        return {
            "recent": recent_payload,
            "failedRecent": failed_payload,
            "latestByCommand": latest_by_command,
            "lastSuccessfulRender": last_successful_render,
            "lastSuccessfulUpdate": last_successful_update,
        }

    def _queue_live_payload(self, queue_url: str) -> dict[str, Any]:
        if not queue_url:
            return {"error": "queue_url_missing"}
        try:
            stats = get_queue_live_stats(
                queue_url=queue_url,
                endpoint_url=str(self._ctx.cfg.runtime.queue.endpoint_url or "").strip() or None,
                aws_access_key_id=self._ctx.deps.get("aws_access_key_id"),
                aws_secret_access_key=self._ctx.deps.get("aws_secret_access_key"),
            )
        except Exception as exc:
            return {"queue_name": queue_url.rstrip("/").rsplit("/", 1)[-1], "error": str(exc)}
        return stats.to_dict()

    def _build_payload(self, env_name: str) -> dict[str, Any]:
        function_name = str(
            self._ctx.cfg.deploy.yandex_cloud.function_name_prod
            if env_name == "prod"
            else self._ctx.cfg.deploy.yandex_cloud.function_name_test
        ).strip()
        try:
            info = get_function_build_info(
                folder_id=str(self._ctx.cfg.deploy.yandex_cloud.folder_id).strip(),
                function_name=function_name,
                sa_json_credentials=self._ctx.deps.get("ydb_sa_json_credentials"),
                sa_key_file=self._ctx.deps.get("ydb_sa_key_file"),
            )
        except Exception as exc:
            return {"functionName": function_name, "error": str(exc)}
        return {
            "functionName": info.function_name,
            "activeVersionId": info.active_version_id,
            "deployedAt": info.deployed_at,
            "runtime": info.runtime,
            "memory": info.memory,
            "timeoutSeconds": info.timeout_seconds,
            "entrypoint": info.entrypoint,
            "serviceAccountId": info.service_account_id,
        }

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
        queue_cfg = self._ctx.cfg.runtime.queue
        telegram_cfg = self._ctx.cfg.runtime.telegram
        raw_key = str(snap_cfg.prefix_raw).replace("{env}", env_name)
        root_prefix = self._resolve_root_prefix(raw_key)
        storage = self._storage_stats(str(snap_cfg.bucket), root_prefix)
        queue_url = str(queue_cfg.prod_queue_url if env_name == "prod" else queue_cfg.test_queue_url).strip()
        queue_name = queue_url.rstrip("/").rsplit("/", 1)[-1] if queue_url else ""
        webhook_path = str(telegram_cfg.webhook_path or "/telegram").strip() or "/telegram"
        api_domain = str(
            self._ctx.cfg.runtime.web.get("api_domain_prod" if env_name == "prod" else "api_domain_test", "")
        ).strip()
        webhook_url = f"https://{api_domain}{webhook_path}" if api_domain else webhook_path
        status_store = self._ctx.deps.get("job_status_store")
        jobs_payload = {
            "recent": [],
            "failedRecent": [],
            "latestByCommand": {},
            "lastSuccessfulRender": None,
            "lastSuccessfulUpdate": None,
        }
        latest_jobs: dict[str, Any] = {}
        if status_store is not None:
            jobs_payload = self._recent_jobs_payload(status_store)
            latest_jobs = self._latest_jobs_payload(status_store)
            merged_latest = dict(jobs_payload.get("latestByCommand", {}) or {})
            merged_latest.update(latest_jobs)
            jobs_payload["latestByCommand"] = merged_latest
        queue_live = self._queue_live_payload(queue_url) if bool(queue_cfg.enabled) else {}
        build_payload = self._build_payload(env_name)
        latest_render = None
        latest_by_command = dict(jobs_payload.get("latestByCommand", {}) or {})
        prometheus_cfg = getattr(self._ctx.cfg.runtime, "prometheus", None)
        grafana_cfg = getattr(self._ctx.cfg.runtime, "grafana", None)
        if isinstance(latest_by_command, dict):
            candidate = latest_by_command.get("render_timeline_sheet")
            if isinstance(candidate, dict):
                latest_render = JobStatusRecord(
                    job_id=str(candidate.get("jobId", "")).strip(),
                    command_type=str(candidate.get("commandType", "render_timeline_sheet")).strip(),
                    status=str(candidate.get("status", "")).strip(),
                    requested_at_utc=datetime.fromisoformat(
                        str(candidate.get("requestedAt", "")).replace("Z", "+00:00")
                    ) if str(candidate.get("requestedAt", "")).strip() else datetime.now(timezone.utc),
                    started_at_utc=datetime.fromisoformat(
                        str(candidate.get("startedAt", "")).replace("Z", "+00:00")
                    ) if str(candidate.get("startedAt", "")).strip() else None,
                    finished_at_utc=datetime.fromisoformat(
                        str(candidate.get("finishedAt", "")).replace("Z", "+00:00")
                    ) if str(candidate.get("finishedAt", "")).strip() else None,
                    requested_by=dict(candidate.get("requestedBy", {}) or {}),
                    summary=dict(candidate.get("summary", {}) or {}),
                    warnings=[str(item) for item in list(candidate.get("warnings", []) or [])],
                    retryable=bool(candidate.get("retryable", False)),
                    error=dict(candidate.get("error", {}) or {}) or None,
                )
        render_debug = _render_debug_payload(latest_render)
        telemetry_payload = {
            "metricsEnabled": self._ctx.deps.get("metrics_client") is not None,
            "metricsClient": type(self._ctx.deps.get("metrics_client")).__name__,
            "monitoringEnabled": bool(
                getattr(self._ctx.cfg.runtime, "monitoring", None)
                and self._ctx.cfg.runtime.monitoring.enabled
            ),
            "monitoringBackend": str(getattr(self._ctx.cfg.runtime.monitoring, "backend", "") or ""),
            "monitoringFolderId": str(getattr(self._ctx.cfg.runtime.monitoring, "folder_id", "") or "").strip()
            or str(self._ctx.cfg.deploy.yandex_cloud.folder_id or "").strip(),
            "dashboardName": str(
                self._ctx.cfg.runtime.monitoring.dashboard_name_prod
                if env_name == "prod"
                else self._ctx.cfg.runtime.monitoring.dashboard_name_test
            ).strip(),
            "dashboardId": str(
                self._ctx.cfg.runtime.monitoring.dashboard_id_prod
                if env_name == "prod"
                else self._ctx.cfg.runtime.monitoring.dashboard_id_test
            ).strip(),
            "datalensEnabled": bool(
                getattr(self._ctx.cfg.runtime, "datalens", None)
                and self._ctx.cfg.runtime.datalens.enabled
            ),
            "datalensOrgId": str(getattr(self._ctx.cfg.runtime.datalens, "org_id", "") or "").strip(),
            "datalensWorkbookName": str(
                getattr(self._ctx.cfg.runtime.datalens, "workbook_name", "") or ""
            ).strip(),
            "datalensWorkbookId": str(
                self._ctx.cfg.runtime.datalens.workbook_id_prod
                if env_name == "prod"
                else self._ctx.cfg.runtime.datalens.workbook_id_test
            ).strip(),
            "datalensConnectionName": str(
                self._ctx.cfg.runtime.datalens.connection_name_prod
                if env_name == "prod"
                else self._ctx.cfg.runtime.datalens.connection_name_test
            ).strip(),
            "datalensConnectionId": str(
                self._ctx.cfg.runtime.datalens.connection_id_prod
                if env_name == "prod"
                else self._ctx.cfg.runtime.datalens.connection_id_test
            ).strip(),
            "datalensDashboardName": str(
                self._ctx.cfg.runtime.datalens.dashboard_name_prod
                if env_name == "prod"
                else self._ctx.cfg.runtime.datalens.dashboard_name_test
            ).strip(),
            "datalensDashboardId": str(
                self._ctx.cfg.runtime.datalens.dashboard_id_prod
                if env_name == "prod"
                else self._ctx.cfg.runtime.datalens.dashboard_id_test
            ).strip(),
            "datalensDashboardUrl": str(
                self._ctx.cfg.runtime.datalens.dashboard_url_prod
                if env_name == "prod"
                else self._ctx.cfg.runtime.datalens.dashboard_url_test
            ).strip(),
            "prometheusEnabled": bool(prometheus_cfg and getattr(prometheus_cfg, "enabled", False)),
            "prometheusBackend": str(getattr(prometheus_cfg, "backend", "") or "").strip(),
            "prometheusEndpointWrite": str(getattr(prometheus_cfg, "endpoint_write", "") or "").strip(),
            "prometheusWorkspaceId": str(
                getattr(prometheus_cfg, "workspace_id_prod", "")
                if env_name == "prod"
                else getattr(prometheus_cfg, "workspace_id_test", "")
            ).strip(),
            "grafanaEnabled": bool(grafana_cfg and getattr(grafana_cfg, "enabled", False)),
            "grafanaBaseUrl": str(getattr(grafana_cfg, "public_base_url", "") or "").strip(),
            "grafanaDashboardUid": str(
                getattr(grafana_cfg, "dashboard_uid_prod", "")
                if env_name == "prod"
                else getattr(grafana_cfg, "dashboard_uid_test", "")
            ).strip(),
            "grafanaDashboardUrl": str(
                getattr(grafana_cfg, "dashboard_url_prod", "")
                if env_name == "prod"
                else getattr(grafana_cfg, "dashboard_url_test", "")
            ).strip(),
            "grafanaEmbedUrl": str(
                getattr(grafana_cfg, "embed_url_prod", "")
                if env_name == "prod"
                else getattr(grafana_cfg, "embed_url_test", "")
            ).strip(),
            "structuredLoggerEnabled": self._ctx.deps.get("structured_logger") is not None,
            "structuredLogger": type(self._ctx.deps.get("structured_logger")).__name__,
        }
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
            "queue": {
                "enabled": bool(queue_cfg.enabled),
                "provider": str(queue_cfg.provider),
                "queueName": queue_name,
                "endpointUrl": str(queue_cfg.endpoint_url or ""),
                "policy": {
                    "retryModel": "queue_driven",
                    "batchPolicy": "per_message",
                    "terminalStatuses": ["failed_terminal"],
                    "retryableStatuses": ["failed_retryable"],
                },
                "latest": latest_by_command,
                "live": queue_live,
            },
            "build": build_payload,
            "jobs": jobs_payload,
            "renderDebug": render_debug,
            "telemetry": telemetry_payload,
            "telegram": {
                "webhookPath": webhook_path,
                "webhookUrl": webhook_url,
                "allowedUpdates": list(telegram_cfg.allowed_updates or []),
                "maxConnections": int(telegram_cfg.max_connections),
                "secretRequired": bool(telegram_cfg.secret_required),
                "secretConfigured": bool(str(self._ctx.deps.get("tg_webhook_secret_token", "")).strip()),
            },
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
