# ⚙️ Tech Rules Document (techrules.md)

## 📌 Project Title
Voice-to-GFG Connect Auto Posting System

---

## 🎯 Purpose
Define a consistent, scalable, and cost-effective technology stack and development rules for the project.

---

## 🧠 Core Principles

- ✅ Zero-cost / minimal-cost tools
- ✅ Reliability over hype
- ✅ Simplicity first, then automation
- ✅ Modular architecture (each component independent)
- ✅ Easy debugging and maintenance

---

## 🏗️ Architecture Overview

Voice Input → Text Processing → AI Formatting → Automation Engine → Browser Execution

---

## 🧩 Tech Stack (Finalized)

### 1. Input Layer (Voice → Text)

| Component | Tool | Reason |
|----------|------|--------|
| Speech Input | Gboard / Windows Dictation | Free, accurate, no setup |
| Optional Upgrade | Whisper (local) | Offline capability |

---

### 2. Processing Layer (Text → Structured Post)

| Component | Tool | Reason |
|----------|------|--------|
| AI Writing | ChatGPT (Free) | No API cost |
| Prompt Templates | Custom prompts | Ensures consistency |

---

### 3. Automation Layer (Core Engine)

| Component | Tool | Reason |
|----------|------|--------|
| Language | Python | Simple + powerful |
| Automation Framework | Playwright | More reliable than Selenium |
| Package Manager | pip | Standard |

---

### 4. Browser Control

| Component | Tool | Reason |
|----------|------|--------|
| Browser | Chromium (via Playwright) | Fast + stable |
| Mode | Headed (headless=False) | Debug visibility |

---

### 5. Interface Layer

| Component | Tool | Reason |
|----------|------|--------|
| CLI | Python input/output | Simple MVP |
| Optional GUI | Tkinter | Lightweight GUI |

---

### 6. Data Handling

| Component | Tool | Reason |
|----------|------|--------|
| Clipboard | pyperclip | Fast text transfer |
| Storage | Local files (.txt/.md) | No DB needed initially |

---

## ⚙️ Development Rules

### Rule 1: Avoid Paid APIs
- No dependency on paid services
- Ensure full functionality without subscriptions

---

### Rule 2: Modular Code Structure

```
project/
│
├── input/
├── processing/
├── automation/
├── utils/
└── main.py
```

---

### Rule 3: Keep Automation Stable
- Use Playwright selectors carefully
- Avoid dynamic selectors
- Re-test after UI changes

---

### Rule 4: Manual Checkpoint (Mandatory)
- Always include confirmation before posting
- Prevent accidental posts

---

### Rule 5: Logging

- Log:
  - Errors
  - Posting success/failure
- Use simple logging (print / logging module)

---

### Rule 6: Session Handling

- Do not automate login initially
- Use persistent browser session
- Upgrade later if needed

---

## 🔐 Security Considerations

- Do not store credentials in code
- Avoid hardcoding sensitive data
- Use manual login for MVP

---

## 📈 Scalability Plan

### Phase 1 (MVP)
- CLI-based
- Manual AI + automation

---

### Phase 2
- Add GUI
- Add clipboard automation

---

### Phase 3
- Multi-platform posting (LinkedIn, etc.)
- Scheduling system

---

### Phase 4 (Advanced)
- Local AI (offline)
- Fully automated pipeline

---

## 🚫 Tech to Avoid (for now)

- ❌ Full AI agents (unstable)
- ❌ Complex frameworks (overkill)
- ❌ Paid APIs
- ❌ Heavy frontend frameworks (React, Angular)

---

## ✅ Final Stack Summary

- Python + Playwright (core)
- ChatGPT (manual AI)
- OS Voice Input
- CLI Interface

---

## 🧠 Key Philosophy

> Build something that works daily, not something that looks impressive but breaks.

---

## 🎯 Outcome

A system that is:
- Reliable
- Maintainable
- Cost-free
- Scalable step-by-step
