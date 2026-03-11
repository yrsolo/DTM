# Grafana VPS Setup

## Purpose

This file is the practical runbook for bringing up Grafana on the owner's VPS for the DTM operator dashboard.

It is intentionally operational and step-by-step.

## Recommended deployment modes

There are two viable modes.

### Mode A - Grafana on VPS + external Prometheus-compatible datasource

Use this when:

- a real Yandex Managed Service for Prometheus workspace and ingestion endpoint are confirmed
- or another external Prometheus-compatible backend is already available

Pros:

- Grafana remains stateless on the VPS
- metrics storage stays outside the VM

### Mode B - Grafana on VPS + VictoriaMetrics on the same VPS

Use this when:

- Yandex Managed Prometheus is still unresolved
- or you want the fastest practical path to a working dashboard

Pros:

- simplest operational rollout
- no dependency on unresolved Yandex Prometheus API/service-point details
- Grafana path and dashboard spec remain the same

Current selected path for the active CAM:

- use **Mode A** with Yandex Managed Service for Prometheus
- keep **Mode B** only as fallback if YMP rollout proves operationally blocked
- exact workspace/datasource steps are documented in:
  - [yandex_prometheus_workspace_setup.md](n:\PROJECTS\python\SCRIPT\DTM\docs\system\yandex_prometheus_workspace_setup.md)

## Inputs you need before touching the VPS

1. VPS public address
2. working SSH access
3. chosen mode:
   - external Prometheus-compatible datasource
   - or local VictoriaMetrics
4. Grafana public base URL you want to expose
5. dashboard JSON from repo:

```powershell
python scripts/render_grafana_dashboard.py --env test --output work/tmp/dtm_test_ops_dashboard.json
```

## Base assumptions

The commands below assume:

- Debian/Ubuntu-like Linux
- `sudo` available
- systemd available
- reverse proxy via Nginx

If the VPS uses another distro, adapt package commands only. The Grafana/VictoriaMetrics logic stays the same.

---

## Part 1 - Base VPS preparation

### 1. Update the host

```bash
sudo apt-get update
sudo apt-get upgrade -y
```

### 2. Install baseline packages

```bash
sudo apt-get install -y curl wget gnupg2 ca-certificates software-properties-common nginx
```

### 3. Open firewall only for what you actually use

If `ufw` is enabled:

```bash
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

Do not expose Grafana or VictoriaMetrics directly on the public network if Nginx is in front.

---

## Part 2 - Install Grafana

### 1. Add Grafana APT repository

```bash
sudo mkdir -p /etc/apt/keyrings
wget -q -O - https://apt.grafana.com/gpg.key | sudo gpg --dearmor -o /etc/apt/keyrings/grafana.gpg
echo "deb [signed-by=/etc/apt/keyrings/grafana.gpg] https://apt.grafana.com stable main" | sudo tee /etc/apt/sources.list.d/grafana.list
sudo apt-get update
```

### 2. Install Grafana

```bash
sudo apt-get install -y grafana
```

### 3. Enable and start Grafana

```bash
sudo systemctl enable grafana-server
sudo systemctl start grafana-server
sudo systemctl status grafana-server --no-pager
```

Grafana default local port:

- `3000`

---

## Part 3A - External Prometheus-compatible datasource

Use this only if you already have a working Prometheus-compatible endpoint.

### 1. Record datasource values

You need:

- datasource URL
- access mode
- auth details if required
- for the selected YMP path:
  - query endpoint for the real workspace
  - bearer token built from `YANDEX_PROMETHEUS_API_KEY`

For repo metadata, also be ready to fill:

- `grafana.public_base_url`
- `grafana.dashboard_uid_test`
- `grafana.dashboard_url_test`
- `grafana.embed_url_test`

### 2. Create datasource in Grafana UI

Grafana UI path:

- `Connections` -> `Data sources` -> `Add data source` -> `Prometheus`

Set:

- name = `DTM YMP Test`
- URL = your Prometheus-compatible query endpoint
- access = `Server`
- auth header = `Authorization: Bearer <YANDEX_PROMETHEUS_API_KEY>`

Save and test.

If this fails, stop there. Grafana dashboard import is pointless until datasource works.

Repo-assisted alternative:

```powershell
python scripts/provision_grafana_datasource.py --env test --workspace-id <workspace_id>
```

---

## Part 3B - Local VictoriaMetrics fallback on the VPS

This is the practical fallback if external Prometheus remains unresolved.

### 1. Download VictoriaMetrics single binary

Example:

```bash
cd /tmp
wget https://github.com/VictoriaMetrics/VictoriaMetrics/releases/latest/download/victoria-metrics-linux-amd64-v1.111.0.tar.gz
tar -xzf victoria-metrics-linux-amd64-v1.111.0.tar.gz
sudo install -m 0755 victoria-metrics-prod /usr/local/bin/victoria-metrics
```

### 2. Create storage directory

```bash
sudo mkdir -p /var/lib/victoria-metrics
sudo chown -R grafana:grafana /var/lib/victoria-metrics || true
```

### 3. Create systemd service

Create `/etc/systemd/system/victoria-metrics.service`:

```ini
[Unit]
Description=VictoriaMetrics
After=network-online.target
Wants=network-online.target

[Service]
User=root
Group=root
ExecStart=/usr/local/bin/victoria-metrics -storageDataPath=/var/lib/victoria-metrics -httpListenAddr=127.0.0.1:8428
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Then:

```bash
sudo systemctl daemon-reload
sudo systemctl enable victoria-metrics
sudo systemctl start victoria-metrics
sudo systemctl status victoria-metrics --no-pager
```

### 4. Add VictoriaMetrics as Grafana datasource

In Grafana:

- datasource type: `Prometheus`
- URL: `http://127.0.0.1:8428`
- access: `Server`

Save and test.

### 5. Point DTM runtime to VictoriaMetrics ingest endpoint

For VictoriaMetrics single-node ingestion, the write endpoint is usually:

- `http://<vps-host>:8428/api/v1/import/prometheus`

If you keep it behind Nginx, expose a proxied internal path instead of raw port `8428`.

Then in DTM runtime config:

- `prometheus.enabled=true`
- `prometheus.endpoint_write=<your chosen URL>`

This mode is often the fastest way to unblock Grafana.

---

## Part 4 - Nginx reverse proxy for Grafana

### 1. Create proxy config

Example `/etc/nginx/sites-available/grafana`:

```nginx
server {
    listen 80;
    server_name YOUR_GRAFANA_HOST;

    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable:

```bash
sudo ln -s /etc/nginx/sites-available/grafana /etc/nginx/sites-enabled/grafana
sudo nginx -t
sudo systemctl reload nginx
```

### 2. Optional TLS

If you have a domain, add TLS with certbot or your existing TLS flow before embedding dashboards publicly.

---

## Part 5 - Grafana hardening for iframe embed

Edit `/etc/grafana/grafana.ini`:

```ini
[server]
root_url = https://YOUR_GRAFANA_HOST

[security]
allow_embedding = true

[auth.anonymous]
enabled = false
org_role = Viewer
```

Notes:

- for the current repo path, prefer Grafana **externally shared/public dashboard** instead of Grafana-wide anonymous access
- keep admin access authenticated
- for iframe embed, the critical server-side toggle is `allow_embedding = true`
- later for `prod`, keep using a tighter share model rather than broad anonymous instance access

Then restart:

```bash
sudo systemctl restart grafana-server
```

---

## Part 6 - Import dashboard from repo

### 1. Render dashboard JSON locally

From the repo:

```powershell
python scripts/render_grafana_dashboard.py --env test --output work/tmp/dtm_test_ops_dashboard.json
```

### 2. Upload the JSON to the VPS or your workstation browser machine

### 3. Import in Grafana UI

Grafana UI:

- `Dashboards` -> `New` -> `Import`
- upload `dtm_test_ops_dashboard.json`
- choose the Prometheus datasource

### 4. Save dashboard

Expected dashboard title:

- `DTM Test Ops`

Expected dashboard UID:

- `dtm-test-ops`

Do not rename it arbitrarily. Repo metadata depends on stable naming.

---

## Part 7 - What to fill back into DTM config

After Grafana dashboard exists, fill these values in `config/runtime.yaml`:

```yaml
grafana:
  enabled: true
  public_base_url: https://YOUR_GRAFANA_HOST
  dashboard_uid_test: dtm-test-ops
  dashboard_url_test: https://YOUR_GRAFANA_HOST/public-dashboards/<public_uid>
  embed_url_test: https://YOUR_GRAFANA_HOST/public-dashboards/<public_uid>?kiosk&theme=light
```

Also set Prometheus section values that match your chosen datasource path.

Then `/info` will be able to expose:

- `grafanaDashboardUrl`
- `grafanaEmbedUrl`
- Prometheus metadata

Current test values already recorded in repo:

- `public_base_url = https://dtm.solofarm.ru/ops/grafana`
- `dashboard_uid_test = dtm-test-ops`
- `dashboard_url_test = https://dtm.solofarm.ru/ops/grafana/public-dashboards/af7606b66c8d4ca9b069ea1913577e45`
- `embed_url_test = https://dtm.solofarm.ru/ops/grafana/public-dashboards/af7606b66c8d4ca9b069ea1913577e45?kiosk&theme=light`

---

## Part 8 - Verification checklist

After setup, verify in this order:

### A. Grafana itself

1. Grafana opens in browser
2. login works
3. datasource `Save & test` works

### B. Metrics ingestion

Trigger from DTM:

1. one API request
2. one snapshot update
3. one render

Then verify dashboard panels are non-empty for:

- Snapshot Stage Timings
- Snapshot Total Duration
- Render Stage Timings
- Render Total Duration
- API Latency
- Worker Reliability

### C. Embed

Open the `dashboard_url_test` in a browser and verify it renders without login.

Then open the `embed_url_test` in iframe or browser and verify it renders.

If iframe still fails and response headers contain `X-Frame-Options: deny`, set:

```ini
[security]
allow_embedding = true
```

and restart Grafana:

```bash
sudo systemctl restart grafana-server
```

---

## Part 9 - Recommended fastest path right now

Because current blockers are:

1. unresolved Yandex Managed Prometheus service point
2. blocked SSH to the VPS

the fastest practical path after SSH is restored is:

1. install Grafana
2. install VictoriaMetrics locally on the same VPS
3. point DTM Prometheus sink to VictoriaMetrics
4. import dashboard JSON from repo
5. verify iframe

Later, if Yandex Managed Prometheus becomes straightforward, you can switch only the datasource and sink endpoint without redesigning the dashboard.

