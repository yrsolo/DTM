    function pretty(value){
      if (typeof value === 'string') {
        try {
          return JSON.stringify(JSON.parse(value), null, 2);
        } catch (_e) {
          return value;
        }
      }
      return JSON.stringify(value, null, 2);
    }
    function formatUtcAndMsk(value){
      const text = String(value || '').trim();
      if (!text) return '';
      const date = new Date(text);
      if (Number.isNaN(date.getTime())) return text;
      const utc = date.toISOString();
      const msk = new Intl.DateTimeFormat('ru-RU', {
        timeZone: 'Europe/Moscow',
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: false,
      }).format(date);
      return utc + ' / MSK ' + msk;
    }
    function createTimer(elementId){
      const el = document.getElementById(elementId);
      let startAt = 0;
      let intervalId = null;
      function format(ms){
        const totalSec = ms / 1000.0;
        const mm = Math.floor(totalSec / 60);
        const ss = totalSec - mm * 60;
        const mmStr = String(mm).padStart(2, '0');
        const ssStr = ss.toFixed(1).padStart(4, '0');
        return mmStr + ':' + ssStr;
      }
      return {
        start(){
          startAt = Date.now();
          if (intervalId) clearInterval(intervalId);
          el.textContent = '00:00.0';
          intervalId = setInterval(() => {
            el.textContent = format(Date.now() - startAt);
          }, 100);
        },
        stop(){
          if (intervalId) clearInterval(intervalId);
          intervalId = null;
          el.textContent = format(Date.now() - startAt);
        },
      };
    }
    const adminTimer = createTimer('adminTimer');
    const apiTimer = createTimer('apiTimer');
    function withBase(path){
      const payloadNode = document.getElementById('infoResult');
      let base = '';
      try {
        const parsed = JSON.parse(payloadNode.textContent || '{}');
        base = String(((parsed.web || {}).uiBasePath) || '').trim();
      } catch (_e) {}
      if (!base) return path;
      if (!path.startsWith('/')) return base + '/' + path;
      return base + path;
    }
    async function loadInfo(){
      const r = await fetch(withBase('/info?format=json&view=detail'), {cache:'no-store'});
      const text = await r.text();
      let p = {};
      try {
        p = JSON.parse(text);
      } catch (_e) {
        document.getElementById('infoResult').textContent = 'HTTP ' + r.status + '\\n' + text;
        return;
      }
      const s = p.snapshot || {};
      const c = p.counts || {};
      const st = p.storage || {};
      const q = p.queue || {};
      const ql = q.live || {};
      const b = p.build || {};
      const jobs = p.jobs || {};
      const recent = jobs.recent || [];
      const failed = jobs.failedRecent || [];
      const latestByCommand = jobs.latestByCommand || {};
      const lastRender = latestByCommand.render_timeline_sheet || null;
      const renderDebug = p.renderDebug || {};
      const bottlenecks = p.bottlenecks || {};
      document.getElementById('env').textContent = s.env || '';
      document.getElementById('bucket').textContent = s.bucket || '';
      document.getElementById('sourceId').textContent = s.sourceId || '';
      document.getElementById('sourceHash').textContent = s.sourceHash || '';
      document.getElementById('rawFetchedAt').textContent = formatUtcAndMsk(s.rawFetchedAt);
      document.getElementById('prepBuiltAt').textContent = formatUtcAndMsk(s.prepBuiltAt);
      document.getElementById('tasksTotal').textContent = c.tasksTotal ?? 0;
      document.getElementById('statusCounts').textContent = JSON.stringify(c.byStatus || {});
      document.getElementById('objectsTotal').textContent = st.objectsTotal ?? 0;
      document.getElementById('bytesTotal').textContent = st.bytesTotal ?? 0;
      document.getElementById('bytesHuman').textContent = st.bytesHuman || '';
      document.getElementById('sizeBreakdown').textContent = JSON.stringify(st.byPrefix || {});
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
      document.getElementById('bottleneckLevel').textContent = String(bottlenecks.profilingLevel || '');
      document.getElementById('bottleneckStageEnabled').textContent = String(!!bottlenecks.stageMetricsEnabled);
      document.getElementById('bottleneckDebugEnabled').textContent = String(!!bottlenecks.debugMetricsEnabled);
      document.getElementById('bottleneckTraceCount').textContent = String((bottlenecks.recentApiTraces || []).length);
      document.getElementById('bottleneckDiagnostics').textContent = pretty(bottlenecks);
      document.getElementById('recentJobs').textContent = pretty(recent);
      document.getElementById('recentErrors').textContent = pretty(failed);
      document.getElementById('lastRenderJob').textContent = pretty(lastRender || {});
      document.getElementById('renderDebug').textContent = pretty(renderDebug);
      document.getElementById('infoResult').textContent = pretty(p);
      const telemetry = p.telemetry || {};
      const web = p.web || {};
      const uiBasePath = String(web.uiBasePath || '').trim();
      const grafanaUrl = String(telemetry.grafanaDashboardUrl || '').trim();
      const grafanaEmbedUrl = String(telemetry.grafanaEmbedUrl || '').trim();
      const grafanaLink = document.getElementById('grafanaLink');
      const grafanaFrame = document.getElementById('grafanaFrame');
      const grafanaEmpty = document.getElementById('grafanaEmpty');
      if (grafanaUrl) {
        grafanaLink.href = grafanaUrl;
        grafanaLink.style.display = 'inline';
      } else {
        grafanaLink.removeAttribute('href');
        grafanaLink.style.display = 'none';
      }
      if (grafanaEmbedUrl) {
        grafanaFrame.src = grafanaEmbedUrl;
        grafanaFrame.style.display = 'block';
        grafanaEmpty.style.display = 'none';
      } else {
        grafanaFrame.removeAttribute('src');
        grafanaFrame.style.display = 'none';
        grafanaEmpty.style.display = 'block';
      }
    }
    async function pollJob(jobId){
      for (let attempt = 0; attempt < 60; attempt += 1) {
        const r = await fetch(withBase('/admin/jobs/' + encodeURIComponent(jobId)), {cache:'no-store'});
        const text = await r.text();
        let payload = text;
        try {
          payload = JSON.parse(text);
        } catch (_e) {}
        document.getElementById('adminResult').textContent = 'HTTP ' + r.status + '\\n' + pretty(payload);
        if (r.ok && payload && typeof payload === 'object') {
          const status = String(payload.status || '').toLowerCase();
          if (status === 'success' || status === 'failed_retryable' || status === 'failed_terminal') {
            return;
          }
        }
        await new Promise((resolve) => setTimeout(resolve, 2000));
      }
    }
    async function enqueueAdminCommand(url, payload){
      adminTimer.start();
      const r = await fetch(withBase(url), {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});
      const t = await r.text();
      let parsed = t;
      try {
        parsed = JSON.parse(t);
      } catch (_e) {}
      document.getElementById('adminResult').textContent = 'HTTP '+r.status+'\\n'+pretty(parsed);
      if (r.ok && parsed && typeof parsed === 'object' && parsed.job_id) {
        await pollJob(parsed.job_id);
      }
      adminTimer.stop();
      setTimeout(loadInfo, 1500);
    }
    function selectedTriggerId(){
      return String((document.getElementById('triggerIdValue') || {}).value || '').trim();
    }
    async function enqueueTriggerEmulation(){
      const triggerId = selectedTriggerId();
      await enqueueAdminCommand('/admin/commands/emulate-trigger', {trigger_id: triggerId});
    }
    function setIncludePeople(flag){
      document.getElementById('includePeople').checked = !!flag;
    }
    function setLimit(value){
      document.getElementById('limitValue').value = String(value);
    }
    function setWindowPreset(days){
      const now = new Date();
      const end = new Date(now.getTime() + days * 24 * 60 * 60 * 1000);
      const toIso = (d) => d.toISOString().slice(0,10);
      document.getElementById('windowStart').value = toIso(now);
      document.getElementById('windowEnd').value = toIso(end);
    }
    function clearWindow(){
      document.getElementById('windowStart').value = '';
      document.getElementById('windowEnd').value = '';
    }
    function selectedStatuses(){
      const statuses = [];
      if (document.getElementById('stWork').checked) statuses.push('work');
      if (document.getElementById('stPreDone').checked) statuses.push('pre_done');
      if (document.getElementById('stWait').checked) statuses.push('wait');
      if (document.getElementById('stDone').checked) statuses.push('done');
      return statuses;
    }
    function selectedAccessMode(){
      return document.getElementById('accessMasked').checked ? 'masked' : 'full';
    }
    function selectedApiRoutePath(){
      return document.getElementById('routeDirect').checked ? '/api/v2/frontend' : '/bff/api/v2/frontend';
    }
    function selectedApiRouteLabel(){
      return document.getElementById('routeDirect').checked ? 'direct backend (/api)' : 'browser proxy (/bff/api)';
    }
    function selectedFetchCredentials(){
      return selectedAccessMode() === 'masked' ? 'omit' : 'include';
    }
    function buildApiQuery(){
      const statuses = selectedStatuses();
      const limit = document.getElementById('limitValue').value || '200';
      const includePeople = document.getElementById('includePeople').checked;
      const windowStart = document.getElementById('windowStart').value;
      const windowEnd = document.getElementById('windowEnd').value;
      const q = new URLSearchParams();
      if (statuses.length > 0) q.set('statuses', statuses.join(','));
      q.set('limit', String(limit));
      q.set('include_people', String(includePeople));
      if (windowStart && windowEnd) {
        q.set('window_start', windowStart);
        q.set('window_end', windowEnd);
      }
      return q;
    }
    function refreshApiRequestUrl(){
      const q = buildApiQuery();
      const origin = window.location.origin || '';
      const accessMode = selectedAccessMode();
      const credentials = selectedFetchCredentials();
      const routePath = selectedApiRoutePath();
      document.getElementById('apiRequestUrl').textContent = origin + withBase(routePath + '?') + q.toString();
      document.getElementById('apiRouteMode').textContent = selectedApiRouteLabel();
      document.getElementById('apiAccessMode').textContent = accessMode + ' / credentials=' + credentials;
    }
    async function sendApiBuilder(){
      apiTimer.start();
      const q = buildApiQuery();
      const accessMode = selectedAccessMode();
      const credentials = selectedFetchCredentials();
      const routePath = selectedApiRoutePath();
      const routeLabel = selectedApiRouteLabel();
      const r = await fetch(withBase(routePath + '?')+q.toString(), {
        cache:'no-store',
        credentials: credentials,
      });
      const t = await r.text();
      document.getElementById('apiResult').textContent = 'route=' + routeLabel + ' mode=' + accessMode + ' credentials=' + credentials + '\\nHTTP '+r.status+'\\n'+pretty(t);
      apiTimer.stop();
      refreshApiRequestUrl();
    }
    function applyApiPreset(name){
      if (name === 'active20') {
        setIncludePeople(true);
        setLimit(20);
        document.getElementById('stWork').checked = true;
        document.getElementById('stPreDone').checked = true;
        document.getElementById('stWait').checked = false;
        document.getElementById('stDone').checked = false;
        clearWindow();
      } else if (name === 'done20') {
        setIncludePeople(false);
        setLimit(20);
        document.getElementById('stWork').checked = false;
        document.getElementById('stPreDone').checked = false;
        document.getElementById('stWait').checked = false;
        document.getElementById('stDone').checked = true;
        clearWindow();
      } else if (name === 'all100') {
        setIncludePeople(false);
        setLimit(100);
        document.getElementById('stWork').checked = true;
        document.getElementById('stPreDone').checked = true;
        document.getElementById('stWait').checked = true;
        document.getElementById('stDone').checked = true;
        clearWindow();
      } else if (name === 'window14') {
        setIncludePeople(true);
        setLimit(200);
        document.getElementById('stWork').checked = true;
        document.getElementById('stPreDone').checked = true;
        document.getElementById('stWait').checked = true;
        document.getElementById('stDone').checked = false;
        setWindowPreset(14);
      }
      refreshApiRequestUrl();
    }
    const watchIds = ['includePeople','accessFull','accessMasked','routeBff','routeDirect','limitValue','stWork','stPreDone','stWait','stDone','windowStart','windowEnd'];
    for (const id of watchIds) {
      const el = document.getElementById(id);
      if (el) el.addEventListener('change', refreshApiRequestUrl);
      if (el && el.tagName === 'INPUT' && el.type === 'number') {
        el.addEventListener('input', refreshApiRequestUrl);
      }
    }
    refreshApiRequestUrl();
    loadInfo();
