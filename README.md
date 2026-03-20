# GFG Connect Web Posting Assistant

Create, rewrite, and publish learning posts from a web UI using FastAPI + React + Playwright automation.

The project supports:
1. typed input and backend voice capture,
2. AI rewrite preview,
3. posting to GFG Connect (primary), and
4. optional LinkedIn/Twitter posting modules.

## Features

1. Web UI (desktop + mobile on local network)
2. FastAPI backend with clear REST endpoints
3. Voice listen endpoint for microphone input
4. AI rewrite endpoint for post formatting
5. Session-aware GFG login flow
6. History view with delete-one and clear-all actions
7. Multi-platform selection UI (GFG, LinkedIn, Twitter/X)

## Tech Stack

1. Frontend: React + Vite
2. Backend: FastAPI + Pydantic
3. Automation: Playwright (Chromium)
4. Language: Python 3.10+

## Clone and Setup

### 1. Clone repository

```bash
git clone https://github.com/Amgothvijaykumar/GFGconnect.git
cd GFGconnect
```

### 2. Create and activate virtual environment

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows (PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install Python dependencies

```bash
pip install -r requirements.txt
python -m playwright install chromium
```

### 4. Install frontend dependencies

```bash
cd frontend
npm install
cd ..
```

## Run the Project

Use two terminals.

### Terminal 1: Start backend

```bash
cd /path/to/GFGconnect
source .venv/bin/activate
python -m uvicorn api.server:app --host 0.0.0.0 --port 8000 --reload
```

### Terminal 2: Start frontend

```bash
cd /path/to/GFGconnect/frontend
npm run dev -- --host 0.0.0.0 --port 5173
```

### Open in browser

1. Local desktop: http://localhost:5173
2. Mobile on same Wi-Fi: http://<your-laptop-ip>:5173

## API Endpoints

1. GET /api/health
2. POST /api/rewrite
3. POST /api/listen
4. POST /api/post
5. GET /api/history
6. DELETE /api/history/{filename}
7. DELETE /api/history

## Usage Flow

1. Open Compose tab.
2. Type or tap Speak for voice capture.
3. Tap Rewrite and edit preview.
4. Select platform and login if needed.
5. Tap Post.
6. Check History tab.
7. Delete single history items or clear all.

## Optional CLI Mode

If you still want terminal workflow:

```bash
source .venv/bin/activate
python main.py
python main.py --clipboard
```

## Notes

1. GFG posting is primary and most stable flow.
2. LinkedIn/Twitter may trigger verification challenges that require manual completion.
3. Voice listening endpoint uses the backend machine microphone.
4. Runtime files like history markdown and browser sessions are local data and should not be committed.

## Troubleshooting

### Port already in use

```bash
lsof -ti tcp:8000 | xargs kill -9
lsof -ti tcp:5173 | xargs kill -9
```

### CORS issue from mobile

1. Ensure backend runs on 0.0.0.0.
2. Open frontend via laptop LAN IP (not random host mismatch).
3. Ensure phone and laptop are on same network.

### Backend import or package errors

```bash
source .venv/bin/activate
pip install -r requirements.txt
python -m playwright install chromium
```

## License

MIT
