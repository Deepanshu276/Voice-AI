import json
import os
import uuid
from datetime import datetime

from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from livekit.api import AccessToken, VideoGrants
from sqlalchemy.orm import Session

from database import create_tables, get_db, Appointment, CallSummary

load_dotenv()
create_tables()

app = FastAPI(title="Mykare Voice AI Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/token")
async def get_token(room: str = None):
    """Generate a LiveKit access token for a participant to join a room."""
    if not room:
        room = f"mykare-{uuid.uuid4().hex[:8]}"

    api_key = os.environ.get("LIVEKIT_API_KEY")
    api_secret = os.environ.get("LIVEKIT_API_SECRET")
    livekit_url = os.environ.get("LIVEKIT_URL")

    if not all([api_key, api_secret, livekit_url]):
        raise HTTPException(status_code=500, detail="LiveKit credentials not configured")

    token = (
        AccessToken(api_key=api_key, api_secret=api_secret)
        .with_identity(f"user-{uuid.uuid4().hex[:6]}")
        .with_name("Patient")
        .with_grants(
            VideoGrants(
                room_join=True,
                room=room,
                can_publish=True,
                can_subscribe=True,
            )
        )
        .to_jwt()
    )

    return {"token": token, "room": room, "url": livekit_url}


@app.get("/appointments/{phone_number}")
async def get_appointments(phone_number: str, db: Session = Depends(get_db)):
    appointments = (
        db.query(Appointment)
        .filter(
            Appointment.phone_number == phone_number,
            Appointment.status == "confirmed",
        )
        .all()
    )
    return [
        {
            "id": a.id,
            "name": a.name,
            "date": a.date,
            "time": a.time,
            "reason": a.reason,
            "status": a.status,
            "created_at": a.created_at.isoformat(),
        }
        for a in appointments
    ]


@app.get("/summary/{room_id}")
async def get_summary(room_id: str, db: Session = Depends(get_db)):
    record = (
        db.query(CallSummary)
        .filter(CallSummary.room_id == room_id)
        .order_by(CallSummary.created_at.desc())
        .first()
    )
    if not record:
        raise HTTPException(status_code=404, detail="Summary not found")
    return {
        "room_id": record.room_id,
        "summary": record.summary,
        "appointments": json.loads(record.appointments),
        "preferences": record.preferences,
        "phone_number": record.phone_number,
        "timestamp": record.created_at.isoformat(),
    }


@app.get("/health")
async def health():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}
