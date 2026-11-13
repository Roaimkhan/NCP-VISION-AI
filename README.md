# NCP Vision

This project is a minimal synthetic demo for the NCP-VISION prototype. The app includes a citizen submission flow, officer dashboard, and public tracking page.

## Prerequisites

- Python 3.11+
- Node.js 18+
- npm
- A terminal with access to the project folder

## 1) Install dependencies

From the project root:

```bash
python3 -m venv .venv
./.venv/bin/pip install --upgrade pip
./.venv/bin/pip install -r backend/requirements.txt
cd frontend && npm install && npm install recharts
```

If you prefer the Makefile shortcut:

```bash
make setup
```

## 2) Start the backend

In one terminal, from the project root:

```bash
cd backend
../.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Or:

```bash
make dev-backend
```

The backend will create the SQLite database automatically on first run and seed demo users/data.

## 3) Start the frontend

In a second terminal, from the project root:

```bash
cd frontend
npm run dev -- --hostname 0.0.0.0 --port 3000
```

Or:

```bash
make dev-frontend
```

## 4) Open the app

Visit:

- http://localhost:3000

The landing page includes the required synthetic-data banner and links to the login and tracking flows.

## 5) Demo accounts

Use these credentials on the login page:

- Citizen: `citizen1` / `demo123`
- Officer: `officer1` / `demo123`
- Admin: `admin1` / `demo123`

## 6) Public tracking

You can check a submitted application without logging in via:

- http://localhost:3000/track/<tracking-number>

Example:

```text
http://localhost:3000/track/NCP-KP-2026-000001
```

## 7) Useful notes

- The backend API runs on port 8000.
- The frontend runs on port 3000.
- All data is synthetic; the banner is shown on every page.
- If a port is already in use, stop the existing process and retry.
- If you want to run tests:

```bash
./.venv/bin/pytest -q
```

## 8) Stopping the app

In each terminal, press:

```bash
Ctrl+C
```

This project is intentionally a minimal working demo of the compressed scope and is not a full production app.
