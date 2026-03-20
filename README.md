# 🚀 Voice-to-GFG Connect Auto Posting System

A cost-free automation system that allows you to **speak your daily learning**, convert it into a structured post, review it, and automatically publish on **GFG Connect**.

## ✨ Features

- 🎤 **Voice Input** — Use OS dictation (macOS: `Fn Fn`) to speak your learning
- 📋 **Clipboard Support** — Auto-read from clipboard (`--clipboard` mode)
- 🤖 **AI-Assisted Writing** — Generates prompts for ChatGPT (free) to structure your posts
- 🔍 **Review & Confirm** — Always preview before posting
- 🌐 **Browser Automation** — Playwright auto-posts to GFG Connect
- 💾 **Session Persistence** — Login once, post daily without re-logging
- 📊 **Post History** — All posts saved locally with timestamps

## 🏗️ Architecture

```
Voice Input → Text Capture → AI Prompt → Formatted Post → Review → Auto Post
```

## 📋 Prerequisites

- Python 3.10+
- macOS / Windows / Linux

## 🚀 Quick Start

### 1. Setup
```bash
# Clone the repo
git clone https://github.com/Amgothvijaykumar/GFGconnect.git
cd GFGconnect

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
```

### 2. Run
```bash
# Manual text input mode
python main.py

# Clipboard mode (paste from voice dictation)
python main.py --clipboard

# Prompt-only mode (just generate AI prompt, no posting)
python main.py --prompt-only
```

## 🌐 Web + Mobile Control (React + API)

Use this mode to manage rewrite/post/history from your phone browser.

### 1. Start backend API
```bash
pip install -r requirements.txt
uvicorn api.server:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Start React frontend
```bash
cd frontend
npm install
npm run dev -- --host 0.0.0.0 --port 5173
```

### 3. Open from mobile
- Ensure mobile and laptop are on same Wi-Fi.
- Open: `http://<your-laptop-local-ip>:5173`

API endpoints added:
- `GET /api/health`
- `POST /api/rewrite`
- `POST /api/post`
- `GET /api/history?limit=30`

### 3. Usage Flow
1. **Speak** your learning using voice dictation
2. **Run** the script — it captures your text
3. **Copy** the generated prompt into ChatGPT
4. **Paste** the AI response back
5. **Review** the formatted post
6. **Confirm** → Auto-posted to GFG Connect! 🎉

## 📁 Project Structure

```
GFGconnect/
├── input/              # Voice/text input handling
│   └── text_input.py
├── processing/         # AI prompt templates & formatting
│   └── content.py
├── automation/         # Playwright browser automation
│   └── browser.py
├── utils/              # Logging & helper functions
│   └── helpers.py
├── main.py             # Entry point
├── requirements.txt
└── README.md
```

## 🔧 Tech Stack

| Component | Tool |
|-----------|------|
| Language | Python |
| Automation | Playwright |
| Voice Input | OS Dictation (free) |
| AI Writing | ChatGPT (free) |
| Clipboard | pyperclip |

## 📌 Notes

- **First run**: You'll need to log into GFG Connect manually in the browser window. Your session will be saved for future runs.
- **Selectors**: If GFG Connect updates their UI, the CSS selectors in `automation/browser.py` may need updating.

## 📄 License

MIT
