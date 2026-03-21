## 1. PROJECT SECTION (Resume Format)

**GFGConnect Auto-Poster — Voice-to-Post Web Assistant (AI Rewrite + Playwright Automation)**  
**Tech Stack:** Python, FastAPI, Pydantic, Playwright, React, Vite, JavaScript, Groq API (Llama), Google Gemini API, SpeechRecognition, Uvicorn, HTML, CSS

- **Built** a full-stack local-network posting assistant with a **FastAPI** backend and **React (Vite)** frontend to capture notes, generate AI rewrites, and publish to social platforms via a single workflow.
- **Implemented** an AI rewrite service (`POST /api/rewrite`) using a structured prompt + provider fallback (**Groq Llama via `groq`**, fallback to **Gemini via `google-genai`**) with environment/.env key loading and output sanitization.
- **Developed** a voice input endpoint (`POST /api/listen`) that performs backend-side speech-to-text using **SpeechRecognition** (Google recognizer) with configurable timeouts for reliable capture in noisy/variable sessions.
- **Engineered** resilient UI automation for GeeksforGeeks Connect posting using **Playwright persistent browser contexts** (session reuse via `browser_data/`), including login detection, credential-based login, editor discovery, and automated publish submission.
- **Designed** an auditable posting trail via filesystem-based history: persisted post attempts as timestamped **Markdown** entries and exposed management APIs (`GET/DELETE /api/history`) with safe filename handling and CORS configured for LAN/mobile access.

---

## 2. TECHNICAL SKILLS SECTION

**Languages:**  
Python, JavaScript, HTML, CSS

**Frameworks/Libraries:**  
FastAPI, Pydantic, React, SpeechRecognition, Playwright

**Tools/Platforms:**  
Vite, Uvicorn, Chromium (Playwright), Groq API, Google Gemini API

**Databases:**  
None (filesystem-based Markdown history store)

**Concepts:**  
REST APIs, GenAI prompt engineering, LLM provider fallback strategy, browser automation (RPA), persistent session management, CORS configuration, client-side state persistence (localStorage), structured request/response validation, error handling and API status modeling, backend speech-to-text pipeline, audit logging/history retention
