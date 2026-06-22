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

## Cost per call breakdown

Approximate cost for a typical **4-minute** booking call (10 conversational turns). Actual pricing changes over time — check each provider's pricing page for current rates.

| Service | Rate (approx.) | Usage in a 4-min call | Est. cost |
|---------|---------------|------------------------|-----------|
| Deepgram STT (nova-2) | $0.0043/min | 4 min of user audio | $0.017 |
| Deepgram TTS (Aura) | ~$0.030 / 1,000 chars | ~2,800 chars spoken by Aria | $0.084 |
| Groq LLM (llama-3.3-70b) | $0.59/1M input, $0.79/1M output tokens | ~6,000 input + 1,200 output tokens (cumulative context) | $0.005 |
| LiveKit Cloud | Free tier: 5,000 participant-min/month, then ~$0.006/participant-min | 4 min × 2 participants = 8 participant-min | $0.00 (within free tier) / ~$0.05 beyond it |

**Estimated total: ~$0.11 per call** (or ~$0.06 if LiveKit usage stays within the free tier).

This scales roughly linearly with call length — longer calls cost more mainly on the TTS and LLM context side, since conversation history grows with each turn.

---

## Smart edge-case handling

The following edge cases are handled at the code level (see [tools.py](backend/tools.py)), not just left to LLM judgment:

- **Double booking** — `book_appointment` and `modify_appointment` check for an existing `confirmed` row at the same date/time before writing, and return a clear error instead of overwriting.
- **Cancelling a non-existent or already-cancelled appointment** — `cancel_appointment` checks both cases and returns a specific error message rather than silently succeeding.
- **Modifying a non-existent appointment** — `modify_appointment` validates the appointment exists before attempting the reschedule.
- **Returning vs. new patient** — `identify_user` looks up the phone number and tells the agent whether to greet a returning patient by name or onboard a new one.
- **Stale slot suggestions** — `fetch_slots` filters out already-booked times for that date so Aria never offers a slot that's already taken.
- **Cancelled appointments excluded from history** — `retrieve_appointments` only returns `confirmed` rows, so a patient's cancelled bookings don't clutter their appointment list.

Additionally, the system prompt ([prompts.py](backend/prompts.py)) instructs Aria to:
- Suggest the next 2-3 available alternatives immediately when a requested slot is unavailable, rather than just saying "not available."
- Assume the nearest upcoming year when a patient gives a date without one (e.g., "March 5th" → the next March 5th from today).

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
