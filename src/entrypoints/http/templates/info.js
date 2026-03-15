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
    const attachmentTimer = createTimer('attachmentTimer');
    let currentInfoPayload = {};
    let attachmentHarnessState = {
      requestUpload: null,
      uploadResult: null,
      finalizeResult: null,
      lastJobPayload: null,
      lastAttachmentId: '',
    };
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
      currentInfoPayload = p || {};
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
      renderAttachmentHarness(p.attachmentsHarness || {});
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
    function attachmentCurrentConfig(){
      return ((currentInfoPayload || {}).attachmentsHarness) || {};
    }
    function attachmentSetResult(step, status, payload){
      const lines = ['step=' + String(step || ''), 'status=' + String(status || '')];
      const value = payload === undefined ? '' : pretty(payload);
      document.getElementById('attachmentHarnessResult').textContent = lines.join(' | ') + (value ? '\n' + value : '');
    }
    function attachmentSelectedFile(){
      const input = document.getElementById('attachmentFileInput');
      const files = input && input.files ? input.files : [];
      return files && files.length ? files[0] : null;
    }
    function attachmentMimeType(file){
      const mime = String((file || {}).type || '').trim();
      if (mime) return mime;
      const name = String((file || {}).name || '').toLowerCase();
      if (name.endsWith('.docx')) return 'application/vnd.openxmlformats-officedocument.wordprocessingml.document';
      if (name.endsWith('.png')) return 'image/png';
      if (name.endsWith('.jpg') || name.endsWith('.jpeg')) return 'image/jpeg';
      if (name.endsWith('.webp')) return 'image/webp';
      return 'application/octet-stream';
    }
    function renderAttachmentHarness(config){
      document.getElementById('attachmentProbeTaskId').textContent = String(config.probeTaskId || '');
      document.getElementById('attachmentProbeExpectedStatus').textContent = String(config.probeTaskExpectedStatus || '');
      document.getElementById('attachmentProbeAvailable').textContent = String(!!config.probeTaskAvailable);
      document.getElementById('attachmentProbeStatus').textContent = String(config.probeTaskStatus || '');
      document.getElementById('attachmentProbeAttachmentsCount').textContent = String(config.probeAttachmentsTotal ?? 0);
      document.getElementById('attachmentAllowedMimes').textContent = String((config.allowedMimeTypes || []).join(', '));
    }
    async function attachmentFetchJson(url, init){
      const response = await fetch(url, init);
      const text = await response.text();
      let payload = text;
      try {
        payload = JSON.parse(text);
      } catch (_e) {}
      return {response, payload, text};
    }
    async function attachmentRequestUpload(){
      attachmentTimer.start();
      try {
        const config = attachmentCurrentConfig();
        const file = attachmentSelectedFile();
        if (!config.enabled) {
          attachmentSetResult('request-upload', 'disabled', {reason: 'attachment_harness_disabled'});
          return;
        }
        if (!config.probeTaskAvailable) {
          attachmentSetResult('request-upload', 'blocked', {reason: config.failureReason || 'probe_task_unavailable', probeTaskId: config.probeTaskId || ''});
          return;
        }
        if (!file) {
          attachmentSetResult('request-upload', 'blocked', {reason: 'file_required'});
          return;
        }
        const route = (((config.browserRoutes || {}).requestUpload) || '').trim();
        const body = {
          task_id: String(config.probeTaskId || ''),
          filename: String(file.name || ''),
          mime: attachmentMimeType(file),
          size: Number(file.size || 0),
          uploaded_by: 'info_attachment_harness',
        };
        const {response, payload} = await attachmentFetchJson(route, {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          credentials: 'include',
          body: JSON.stringify(body),
        });
        attachmentHarnessState.requestUpload = response.ok && payload && typeof payload === 'object' ? payload : null;
        attachmentHarnessState.uploadResult = null;
        attachmentHarnessState.finalizeResult = null;
        attachmentHarnessState.lastJobPayload = null;
        attachmentHarnessState.lastAttachmentId = String(((attachmentHarnessState.requestUpload || {}).attachment_id) || '');
        attachmentSetResult('request-upload', response.status, payload);
      } catch (error) {
        attachmentSetResult('request-upload', 'failed', {message: String((error || {}).message || error || 'unknown_error')});
      } finally {
        attachmentTimer.stop();
      }
    }
    async function attachmentUploadBinary(){
      attachmentTimer.start();
      try {
        const contract = attachmentHarnessState.requestUpload || {};
        const file = attachmentSelectedFile();
        if (!file) {
          attachmentSetResult('upload-binary', 'blocked', {reason: 'file_required'});
          return;
        }
        if (!contract.uploadUrl) {
          attachmentSetResult('upload-binary', 'blocked', {reason: 'request_upload_required'});
          return;
        }
        const headers = {};
        const sourceHeaders = contract.headers || {};
        for (const [key, value] of Object.entries(sourceHeaders)) {
          headers[String(key)] = String(value);
        }
        const response = await fetch(String(contract.uploadUrl), {
          method: 'PUT',
          headers,
          body: file,
        });
        const text = await response.text();
        attachmentHarnessState.uploadResult = {
          status: response.status,
          ok: response.ok,
          body: text,
          headers,
          diagnostics: contract.diagnostics || {},
        };
        attachmentSetResult('upload-binary', response.status, attachmentHarnessState.uploadResult);
      } catch (error) {
        const contract = attachmentHarnessState.requestUpload || {};
        const diagnostics = contract.diagnostics || {};
        const uploadUrl = String(contract.uploadUrl || '');
        let uploadHost = '';
        try {
          uploadHost = uploadUrl ? new URL(uploadUrl).host : '';
        } catch (_e) {}
        attachmentHarnessState.uploadResult = {
          step: 'upload-binary',
          host: uploadHost,
          method: 'PUT',
          details: String((error || {}).message || error || 'Failed to fetch'),
          uploadHost: uploadHost,
          headerKeys: Object.keys(contract.headers || {}),
          diagnostics,
        };
        attachmentSetResult('upload-binary', 'failed', attachmentHarnessState.uploadResult);
      } finally {
        attachmentTimer.stop();
      }
    }
    async function attachmentFinalize(){
      attachmentTimer.start();
      try {
        const config = attachmentCurrentConfig();
        const contract = attachmentHarnessState.requestUpload || {};
        if (!config.probeTaskId || !contract.attachment_id) {
          attachmentSetResult('finalize', 'blocked', {reason: 'request_upload_required'});
          return;
        }
        const route = (((config.browserRoutes || {}).finalize) || '').trim();
        const {response, payload} = await attachmentFetchJson(route, {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          credentials: 'include',
          body: JSON.stringify({
            task_id: String(config.probeTaskId || ''),
            attachment_id: String(contract.attachment_id || ''),
            uploaded_by: 'info_attachment_harness',
          }),
        });
        attachmentHarnessState.finalizeResult = response.ok && payload && typeof payload === 'object' ? payload : null;
        attachmentSetResult('finalize', response.status, payload);
      } catch (error) {
        attachmentSetResult('finalize', 'failed', {message: String((error || {}).message || error || 'unknown_error')});
      } finally {
        attachmentTimer.stop();
      }
    }
    async function attachmentPollJob(jobId){
      attachmentTimer.start();
      try {
        const config = attachmentCurrentConfig();
        const template = String((((config.browserRoutes || {}).jobStatusTemplate) || '')).trim();
        if (!template || !jobId) {
          attachmentSetResult('job-status', 'blocked', {reason: 'job_id_required'});
          return null;
        }
        const url = template.replace('{job_id}', encodeURIComponent(String(jobId)));
        for (let attempt = 0; attempt < 60; attempt += 1) {
          const {response, payload} = await attachmentFetchJson(url, {cache:'no-store', credentials:'include'});
          attachmentHarnessState.lastJobPayload = payload;
          attachmentSetResult('job-status', response.status, payload);
          if (response.ok && payload && typeof payload === 'object') {
            const status = String(payload.status || '').toLowerCase();
            if (status === 'success' || status === 'failed_retryable' || status === 'failed_terminal') {
              return payload;
            }
          }
          await new Promise((resolve) => setTimeout(resolve, 2000));
        }
        return null;
      } catch (error) {
        attachmentSetResult('job-status', 'failed', {message: String((error || {}).message || error || 'unknown_error')});
        return null;
      } finally {
        attachmentTimer.stop();
      }
    }
    async function attachmentPollLastJob(){
      const finalizePayload = attachmentHarnessState.finalizeResult || {};
      const jobId = String(finalizePayload.job_id || finalizePayload.jobId || '');
      return attachmentPollJob(jobId);
    }
    async function attachmentCheckProbeState(){
      attachmentTimer.start();
      try {
        await loadInfo();
        const config = attachmentCurrentConfig();
        const targetId = String(attachmentHarnessState.lastAttachmentId || '');
        const attachments = Array.isArray(config.probeAttachments) ? config.probeAttachments : [];
        const match = targetId ? attachments.find((item) => String((item || {}).id || '') === targetId) : null;
        attachmentSetResult('frontend-check', 'ok', {
          probeTaskId: config.probeTaskId || '',
          probeTaskAvailable: !!config.probeTaskAvailable,
          probeTaskStatus: config.probeTaskStatus || '',
          probeAttachmentsTotal: config.probeAttachmentsTotal ?? attachments.length,
          targetAttachmentId: targetId,
          targetAttachmentVisible: !!match,
          targetAttachment: match || null,
        });
        return match || null;
      } catch (error) {
        attachmentSetResult('frontend-check', 'failed', {message: String((error || {}).message || error || 'unknown_error')});
        return null;
      } finally {
        attachmentTimer.stop();
      }
    }
    async function attachmentOpenLink(kind){
      attachmentTimer.start();
      try {
        const config = attachmentCurrentConfig();
        const attachmentId = String(attachmentHarnessState.lastAttachmentId || '');
        const browserRoutes = config.browserRoutes || {};
        const template = kind === 'download' ? browserRoutes.downloadTemplate : browserRoutes.viewTemplate;
        if (!template || !attachmentId) {
          attachmentSetResult(kind, 'blocked', {reason: 'attachment_id_required'});
          return;
        }
        const url = String(template).replace('{attachment_id}', encodeURIComponent(attachmentId));
        const response = await fetch(url, {cache:'no-store', credentials:'include', redirect:'manual'});
        const text = await response.text();
        attachmentSetResult(kind, response.status, {
          redirected: response.type === 'opaqueredirect' || response.status === 302 || response.status === 301 || response.status === 307 || response.status === 308,
          location: response.headers.get('Location') || '',
          body: text,
        });
      } catch (error) {
        attachmentSetResult(kind, 'failed', {message: String((error || {}).message || error || 'unknown_error')});
      } finally {
        attachmentTimer.stop();
      }
    }
    async function attachmentOpenView(){
      return attachmentOpenLink('view');
    }
    async function attachmentOpenDownload(){
      return attachmentOpenLink('download');
    }
    async function attachmentDelete(){
      attachmentTimer.start();
      try {
        const config = attachmentCurrentConfig();
        const attachmentId = String(attachmentHarnessState.lastAttachmentId || '');
        if (!config.probeTaskId || !attachmentId) {
          attachmentSetResult('delete', 'blocked', {reason: 'attachment_id_required'});
          return;
        }
        const route = (((config.browserRoutes || {}).delete) || '').trim();
        const {response, payload} = await attachmentFetchJson(route, {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          credentials: 'include',
          body: JSON.stringify({
            task_id: String(config.probeTaskId || ''),
            attachment_id: attachmentId,
            deleted_by: 'info_attachment_harness',
          }),
        });
        attachmentSetResult('delete', response.status, payload);
        if (response.ok && payload && typeof payload === 'object') {
          attachmentHarnessState.finalizeResult = payload;
        }
      } catch (error) {
        attachmentSetResult('delete', 'failed', {message: String((error || {}).message || error || 'unknown_error')});
      } finally {
        attachmentTimer.stop();
      }
    }
    async function attachmentRunFullFlow(){
      await attachmentRequestUpload();
      if (!attachmentHarnessState.requestUpload) return;
      await attachmentUploadBinary();
      if (!attachmentHarnessState.uploadResult || !attachmentHarnessState.uploadResult.ok) return;
      await attachmentFinalize();
      const finalizePayload = attachmentHarnessState.finalizeResult || {};
      if (!finalizePayload.job_id && !finalizePayload.jobId) return;
      await attachmentPollLastJob();
      const visible = await attachmentCheckProbeState();
      if (!visible) return;
      await attachmentOpenView();
      await attachmentOpenDownload();
      await attachmentDelete();
      const deletePayload = attachmentHarnessState.finalizeResult || {};
      if (deletePayload.job_id || deletePayload.jobId) {
        await attachmentPollLastJob();
      }
      await attachmentCheckProbeState();
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
