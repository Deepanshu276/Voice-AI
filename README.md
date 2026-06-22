# Mykare Voice AI Agent

A web-based AI front-desk assistant for healthcare — voice-driven appointment booking with a talking avatar, real-time tool call display, and end-of-call summaries.

## Tech Stack

| Layer | Choice |
|-------|--------|
| Voice | LiveKit Agents |
| STT | Deepgram (nova-2) |
| TTS | Deepgram Aura (aura-asteria-en) |
| LLM | Groq (llama-3.3-70b-versatile) |
| Avatar | CSS animated (no extra API) |
| Backend | FastAPI + Python |
| DB | SQLite (SQLAlchemy) |
| Frontend | Vite + React + TypeScript |

---

## Prerequisites

- Python 3.10+
- Node.js LTS (includes npm) — https://nodejs.org

## Setup

### 1. API Keys needed

| Service | Get key at |
|---------|-----------|
| LiveKit | https://cloud.livekit.io |
| Deepgram | https://console.deepgram.com |
| Groq | https://console.groq.com |

### 2. Backend

```bash
cd project/backend

# Create and activate virtualenv
python -m venv venv
venv\Scripts\activate       # Windows
# source venv/bin/activate  # Mac/Linux

pip install -r requirements.txt

# Configure environment
copy .env.example .env
# Edit .env and fill in all API keys

# Terminal 1 — Start FastAPI server
uvicorn main:app --reload --port 8000

# Terminal 2 — Start LiveKit agent worker
python agent.py dev
```

### 3. Frontend

```bash
cd project/frontend

npm install

# Optional: copy .env.example to .env (defaults to localhost:8000 via Vite proxy)
copy .env.example .env

npm run dev
# Opens at http://localhost:5173
```

---

## Usage

1. Open `http://localhost:5173`
2. Click **Start Voice Call**
3. Allow microphone access
4. Talk to Aria — she will:
   - Ask for your phone number to identify you
   - Book/cancel/modify appointments via voice
   - Show real-time tool call status on screen
5. Say "Goodbye" or "That's all" — Aria generates a call summary within 10 seconds

---

## Features

- **Voice conversation** — Deepgram STT + Deepgram Aura TTS via LiveKit WebRTC
- **Tool calling** — 7 tools: identify_user, fetch_slots, book_appointment, retrieve_appointments, cancel_appointment, modify_appointment, end_conversation
- **Animated avatar** — pulsing rings sync with Aria's speech
- **Live tool status** — every action shown on screen in real time
- **Call summary** — conversation summary + appointment list displayed at end of call
- **Double-booking prevention** — SQLite checks slot conflicts before confirming

---

## Resetting test data

Delete the SQLite file to wipe all appointments/summaries — it's recreated empty on next run:

```bash
cd project/backend
del appointments.db   # Windows
# rm appointments.db  # Mac/Linux
```

---

## Project Structure

```
project/
├── backend/
│   ├── main.py        FastAPI REST API (/token, /summary, /appointments)
│   ├── agent.py       LiveKit agent worker with all tool definitions
│   ├── database.py    SQLite models (Appointment, CallSummary)
│   ├── tools.py       Tool implementations
│   ├── prompts.py     Aria's system prompt
│   └── requirements.txt
└── frontend/
    └── src/
        ├── components/
        │   ├── VoiceInterface.tsx   Main call UI
        │   ├── Avatar.tsx           Animated avatar
        │   ├── ToolStatusPanel.tsx  Live tool events
        │   └── CallSummary.tsx      End-of-call modal
        └── index.css
```
