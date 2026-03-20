# Product Requirements Document (PRD)

## Product Title
GFG Connect Web Posting Assistant (Voice + AI + Automation)

## Objective
Provide a reliable, low-friction system to create and publish learning posts with:
- text or voice input,
- AI rewrite and review,
- one-tap posting via browser automation,
- history tracking and cleanup.

## Target Users
- Students and developers posting regular learning updates.
- Users who want to post from mobile or desktop without manually navigating every step.

## Problem Statement
Manual posting is repetitive and inconsistent:
- users type/rewrite the same type of content daily,
- website navigation and posting consume time,
- session/login state variations make automation brittle.

## Current Solution (Implemented)
The product now runs as a web app with API backend:
1. User enters raw text or taps Speak (backend microphone capture).
2. System rewrites content using AI provider integration.
3. User edits preview.
4. User posts to selected platform (GFG, LinkedIn, Twitter/X).
5. System stores post history as markdown files.
6. User can view, delete one history item, or clear all history.

## Architecture
Frontend (React, Vite)
-> Backend API (FastAPI)
-> Processing (AI rewrite)
-> Automation (Playwright browsers)
-> Target platform web UI (GFG/LinkedIn/Twitter)

## Core Components

### Frontend
- Compose and History tabs
- Platform selector
- Login modal (per platform credentials stored locally)
- Voice trigger button with listening state
- History delete controls

### Backend API
- `GET /api/health`
- `POST /api/rewrite`
- `POST /api/listen`
- `POST /api/post`
- `GET /api/history`
- `DELETE /api/history/{filename}`
- `DELETE /api/history`

### Automation Layer
- `automation/browser.py` for GFG Connect
- `automation/linkedin.py` for LinkedIn
- `automation/twitter.py` for Twitter/X

## Functional Requirements

### FR1 Input
- Accept typed input.
- Accept voice input through backend microphone capture endpoint.

### FR2 Rewrite
- Convert raw input into concise, readable post format.
- Allow user to manually edit final preview.

### FR3 Posting
- Post to selected platform from the same UI.
- Reuse cached sessions when available.

### FR4 Login and Session Handling
- Support explicit credential login flow.
- Avoid unnecessary re-login when session is already active.

### FR5 History Management
- Persist post attempts in local markdown files.
- Show recent history in frontend.
- Support single-item delete and clear-all delete.

## Non-Functional Requirements
- Reliability: tolerate UI variations with robust selector fallbacks.
- Cost: avoid paid dependencies when possible.
- Usability: mobile-friendly UI and minimal posting steps.
- Maintainability: modular Python packages and simple API contracts.

## Known Constraints
- No official posting API from target platforms; browser automation is required.
- LinkedIn/Twitter verification challenges may require manual intervention.
- Platform UI updates can break selectors and need maintenance.

## Success Criteria
- Users can complete create -> rewrite -> post workflow from web UI.
- GFG posting works reliably with cached-session and login-required scenarios.
- History management works end-to-end (read/delete/clear).
- Frontend is usable from local network mobile access.

## Out of Scope (Current Release)
- Background scheduler/queueing for timed posts.
- Enterprise-grade credential vault.
- Full autonomous retry orchestration for all platform failures.

## Next Milestones
1. Add retry/backoff and screenshot capture on failure.
2. Harden LinkedIn/Twitter flows for challenge handling UX.
3. Add filtered history by platform/status.
