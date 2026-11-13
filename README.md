NCP-VISION — Windows Setup Guide

This project is a minimal synthetic demo for the NCP-VISION prototype. The application includes:

- Citizen submission flow
- Officer dashboard
- Public application tracking page

Prerequisites

Install the following:

- Python 3.11+
- Node.js 18+
- npm
- Windows 10/11
- PowerShell

Verify your installations:

python --version
node --version
npm --version

1. Install Dependencies

Open PowerShell and navigate to the project root directory:

cd path\to\NCP-VISION

Create a Python virtual environment:

python -m venv .venv

Upgrade pip:

.\.venv\Scripts\python.exe -m pip install --upgrade pip

Install backend dependencies:

.\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt

Install frontend dependencies:

cd frontend
npm install
npm install recharts
cd ..

2. Start the Backend

Open the first PowerShell terminal.

Navigate to the project root (if necessary):

cd path\to\NCP-VISION

Start the backend:

cd backend
..\.venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

The backend will run on:

http://localhost:8000

The SQLite database will be created automatically on the first run, along with demo users and data.

3. Start the Frontend

Open a second PowerShell terminal.

Navigate to the project root:

cd path\to\NCP-VISION

Start the frontend:

cd frontend
npm run dev -- --hostname 0.0.0.0 --port 3000

The frontend will run on:

http://localhost:3000

4. Open the Application

Open your browser and visit:

http://localhost:3000

The landing page includes:

- Synthetic-data banner
- Login flow
- Public tracking flow

5. Demo Accounts

Use the following credentials on the login page.

Role| Username| Password
Citizen| citizen1| demo123
Officer| officer1| demo123
Admin| admin1| demo123

6. Public Application Tracking

Applications can be tracked without logging in.

Example:

http://localhost:3000/track/NCP-KP-2026-000001

Replace the tracking number with the relevant application tracking number.

7. Run Tests

From the project root:

.\.venv\Scripts\python.exe -m pytest -q

8. Useful Information

Component| Port
Backend API| 8000
Frontend| 3000

Additional notes:

- All application data is synthetic.
- The synthetic-data banner appears on every page.
- The backend uses SQLite.
- Keep both backend and frontend terminals running while using the application.
- If a port is already occupied, stop the process using that port before restarting the application.

9. Stop the Application

In both PowerShell terminals, press:

Ctrl + C

This terminates the respective development server.

---

Important: NCP-VISION is intentionally a minimal working demonstration of the compressed project scope. It is not a full production-ready application.
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
