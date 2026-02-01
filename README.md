# Grafana GitOps Dashboard Manager

A GitOps-based dashboard management system for Grafana that enables  
dashboard **versioning, rollback, and one-click restore** using Git as the source of truth.

Dashboards are exported as JSON, stored in Git, and can be restored from any
previous version via **CLI or Web UI**.

---

## Features

- Export Grafana dashboards as JSON
- Automatically version dashboards in Git
- Detect & skip exports when no changes are found
- List all available dashboard versions
- One-click rollback to any previous version
- Web UI (React) + Backend API (Flask)
- Fully clonable & reproducible setup

---

## Tech Stack

- Grafana
- Python (automation scripts)
- Flask (backend API)
- React + Vite (frontend UI)
- Git (version control)
- Docker / Docker Compose

---

## Project Structure

```text
grafana-gitops/
├── backend/          # Flask backend API
├── frontend/         # React + Vite UI
├── dashboards/       # Versioned Grafana dashboards
├── scripts/          # Export, apply & rollback scripts
├── docker-compose.yml
├── prometheus.yml
└── README.md
```

---

## Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/AadityaDhondkar/grafana-gitops
cd grafana-gitops
```

### 2. Start Grafana & Prometheus
```bash
docker-compose up -d
```

Grafana UI:
```
http://localhost:3000
```

---

### 3. Start Backend (Flask)
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 app.py
```

Backend API:
```
http://localhost:5000
```

---

### 4. Start Frontend (React)
```bash
cd frontend
npm install
npm run dev
```

Frontend UI:
```
http://localhost:5173
```

---

## Dashboard Workflow

### Export Dashboard
- From Web UI → **Export Dashboard**
- Or via CLI:
```bash
python3 scripts/export_dashboard.py
```

A new Git version is created **only if changes are detected**.

---

### Rollback Dashboard
- Select a version from the Web UI
- Click **Apply Selected Version**
- Dashboard is restored via Grafana API

---

## Automation (Optional)

You can automate dashboard export using cron:

```bash
*/5 * * * * python3 scripts/export_dashboard.py
```

This continuously checks for changes and commits **only when required**.

---

