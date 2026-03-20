# Tech Rules (techrules.md)

## Project
GFG Connect Web Posting Assistant

## Purpose
Define implementation rules for a reliable web + API + browser-automation workflow.

## Core Principles
- Reliability over feature count.
- Prefer explicit fallbacks for unstable website selectors.
- Keep architecture modular and debuggable.
- Treat runtime artifacts (history/logs/session/cache) as non-source data.

## Current Stack (Authoritative)

### Frontend
- React + Vite
- Mobile-friendly CSS
- API-driven workflow

### Backend
- FastAPI + Pydantic
- REST endpoints for rewrite/listen/post/history

### Automation
- Playwright (Python)
- Platform modules:
  - `automation/browser.py` (GFG)
  - `automation/linkedin.py`
  - `automation/twitter.py`

### Processing and Input
- AI rewrite module in `processing/`
- Voice and text input helpers in `input/`

### Runtime Storage
- Post history files: `history/*.md`
- Browser session cache: `browser_data/` (local runtime only)

## Repository Rules

### Rule 1: Keep Runtime Data Out of Git
- Do not commit session files, logs, cache, or generated history markdown.
- `.gitignore` must include `.venv/`, `venv/`, `history/*.md`, `browser_data/`, logs and caches.

### Rule 2: API Contract Stability
- Changes to request/response models must be backward compatible when possible.
- Any endpoint behavior change must be reflected in frontend logic.

### Rule 3: Automation Robustness First
- Always use selector fallback arrays for critical actions.
- Verify session state before triggering login.
- Avoid hard dependency on a single UI structure.

### Rule 4: Error Handling Standards
- Return actionable HTTP errors from API.
- Preserve post history status (`posted`, `failed`, `draft`, `cancelled`) for traceability.
- Never swallow exceptions silently in automation layer.

### Rule 5: Security and Credentials
- Never hardcode credentials in source.
- Current UI stores credentials in browser localStorage for convenience; treat as non-production security posture.
- Future production path should move to secure credential storage or token-based flow.

### Rule 6: Frontend UX Consistency
- Keep compose flow simple: input -> rewrite -> edit -> post.
- Keep history actions synchronized with backend state.
- Use clear status messages for long-running actions (listen/post/delete).

### Rule 7: Validation Before Push
- Python files must pass `py_compile` checks.
- Frontend must pass `npm run build`.
- If backend routes change, verify via `/openapi.json` or endpoint checks.

## Architecture Layout (Current)

```
api/
automation/
frontend/
input/
processing/
utils/
main.py
```

## Operational Guidance
- Start backend with virtualenv: `python -m uvicorn api.server:app --host 0.0.0.0 --port 8000 --reload`
- Run frontend dev server from `frontend/`.
- For mobile testing, use same LAN and backend host IP.

## Known Technical Risks
- Platform login challenge/verification can interrupt automation.
- Site UI changes may break selectors.
- Voice endpoint uses backend machine microphone, not remote client microphone.

## Next Technical Priorities
1. Add retry/backoff wrappers for fragile browser actions.
2. Add screenshot-on-failure for faster selector debugging.
3. Improve secure credential strategy for multi-user scenarios.
