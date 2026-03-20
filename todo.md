# TODO.md

## Project
Voice-to-GFG Connect Auto Posting System (now Web + API based)

## Current Status
- Core system is working end-to-end with FastAPI backend + React frontend.
- GFG posting flow is stable with session-aware login and robust editor detection.
- LinkedIn and Twitter posting modules are added (verification/challenge behavior still depends on platform security checks).

## Completed

### Foundation
- [x] Python project structure (`input/`, `processing/`, `automation/`, `utils/`)
- [x] Playwright automation baseline
- [x] Virtual environment setup

### Input and AI Processing
- [x] CLI text input
- [x] Voice input pipeline in backend (`input/text_input.py`)
- [x] Clipboard input support
- [x] AI rewrite integration (`processing/content.py`)

### Web/API Platform
- [x] FastAPI server (`api/server.py`)
- [x] React frontend (`frontend/`)
- [x] Mobile-friendly UI (compose/history/login)
- [x] CORS support for local network usage
- [x] Health endpoint (`/api/health`)
- [x] Rewrite endpoint (`/api/rewrite`)
- [x] Listen endpoint (`/api/listen`)
- [x] Post endpoint (`/api/post`)
- [x] History read endpoint (`/api/history`)
- [x] History delete endpoints (`DELETE /api/history/{filename}`, `DELETE /api/history`)

### Posting and Reliability
- [x] Session-aware GFG login behavior (avoid forced re-login when already authenticated)
- [x] Improved GFG composer/editor detection across UI variants
- [x] Robust post fill + submit flow
- [x] Post history save/read/delete support

### Multi-platform
- [x] Platform selector in UI
- [x] LinkedIn automation module (`automation/linkedin.py`)
- [x] Twitter/X automation module (`automation/twitter.py`)

## In Progress / Needs Real-World Validation
- [ ] Daily usage validation over multiple days
- [ ] Selector stability checks after site UI changes
- [ ] LinkedIn/Twitter challenge/verification handling UX improvements

## Pending Work

### Testing
- [ ] Add repeatable test checklist for:
  - short input
  - long input
  - empty input
  - invalid input
  - login-required scenario
  - cached-session scenario

### Reliability Enhancements
- [ ] Add retry/backoff strategy for recoverable browser actions
- [ ] Add optional screenshot capture on automation failures
- [ ] Improve structured error responses for frontend display

### Product Enhancements
- [ ] Add optional scheduling for queued posts
- [ ] Add per-platform history filters in UI
- [ ] Add secure credential management strategy (avoid plain localStorage)

## Definition of Done (Updated)
- [x] End-to-end workflow functional (input -> rewrite -> post)
- [x] Web UI usable on desktop and mobile
- [x] History management supports read + delete
- [ ] Production-hardening complete (retry + advanced logging + long-run reliability)

## Notes
- Tkinter desktop UI path is intentionally dropped in favor of React + FastAPI.
- `history/*.md` is runtime data and is ignored by git.
