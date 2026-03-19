# 📌 Product Requirements Document (PRD)

## 🧠 Product Title
Voice-to-GFG Connect Auto Posting System

---

## 🎯 Objective
Build a cost-free automation system that allows a user to:
- Speak their daily learning
- Convert it into a structured post
- Review and confirm
- Automatically publish on GFG Connect

---

## 👤 Target User
- Student (AIML / CS)
- Regularly posts learning updates
- Wants consistency without spending time on manual posting

---

## 🚀 Problem Statement
Posting daily updates requires:
- Writing effort
- Editing
- Navigating website manually

This leads to:
- Inconsistency
- Time waste
- Reduced productivity

---

## 💡 Solution Overview
A hybrid system combining:
- Voice input
- AI-assisted writing
- Browser automation

---

## 🔄 User Flow

1. User speaks learning via mic
2. Speech is converted to text
3. AI rewrites into structured post
4. User reviews generated post
5. System asks for confirmation
6. On approval → auto posts to GFG Connect

---

## 🏗️ System Architecture

Voice Input
   ↓
Speech-to-Text (Local / OS)
   ↓
AI Writing (ChatGPT - manual/free)
   ↓
Python Script (Playwright)
   ↓
Browser Automation
   ↓
GFG Connect Post Submission

---

## 🧩 Core Components

### 1. Voice Input
- Tool: Gboard / Windows Dictation
- Output: Raw text

---

### 2. AI Writing Module
- Tool: ChatGPT (Free usage)
- Input: Raw text
- Output: Clean formatted post

---

### 3. Automation Engine
- Tool: Playwright (Python)
- Responsibilities:
  - Open browser
  - Navigate to GFG Connect
  - Fill post content
  - Submit post

---

### 4. Confirmation Layer
- CLI-based input:
  Do you want to post? (yes/no)

---

## ⚙️ Functional Requirements

### FR1: Voice Input
- System should accept spoken input
- Convert to editable text

---

### FR2: Content Generation
- System should convert raw text into:
  - Structured
  - Grammatically correct
  - Short post

---

### FR3: User Confirmation
- System must display generated content
- Ask for approval before posting

---

### FR4: Automated Posting
- System should:
  - Open browser
  - Navigate to GFG Connect
  - Paste content
  - Click post button

---

### FR5: Manual Login Support
- User logs in manually once
- Session should persist

---

## ⚠️ Non-Functional Requirements

### NFR1: Cost
- Must be completely free
- No paid APIs

---

### NFR2: Reliability
- Must work consistently daily
- Should not depend on unstable AI agents

---

### NFR3: Usability
- Simple workflow
- Minimal steps

---

### NFR4: Performance
- Posting should complete within 10–20 seconds

---

## 🛠️ Tech Stack

| Component | Tool |
|----------|------|
| Speech Input | Gboard / Windows Voice |
| AI Writing | ChatGPT (manual/free) |
| Automation | Playwright (Python) |
| UI | CLI (initial version) |

---

## 📉 Limitations

- No direct API for GFG Connect
- Requires browser automation
- UI changes in website may break script
- Voice accuracy depends on device

---

## 🔮 Future Enhancements

- Auto voice-to-text integration (Whisper local)
- GUI interface (Tkinter)
- Auto login session handling
- One-click execution
- Scheduled posting
- Multi-platform posting (LinkedIn, Twitter)

---

## 📊 Success Metrics

- Daily posting consistency (≥ 90%)
- Time saved per post (> 70%)
- Zero manual typing effort
- Successful post rate (> 95%)

---

## 🧪 MVP Scope

Include:
- Manual voice → text
- ChatGPT rewriting
- Playwright posting
- Confirmation step

Exclude:
- Full AI agent automation
- Paid APIs
- Multi-platform posting

---

## 🧠 Key Design Decision

Avoid:
- Over-engineering
- Unstable AI agents

Focus on:
- Simplicity
- Reliability
- Zero cost

---

## ✅ Final Outcome

A lightweight system that enables:
👉 “Speak → Review → Post” in under 1 minute
