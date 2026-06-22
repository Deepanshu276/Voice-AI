import json
from datetime import datetime, timedelta
from database import SessionLocal, Appointment, CallSummary, create_tables

create_tables()

AVAILABLE_SLOTS = [
    "09:00 AM", "09:30 AM", "10:00 AM", "10:30 AM",
    "11:00 AM", "11:30 AM", "02:00 PM", "02:30 PM",
    "03:00 PM", "03:30 PM", "04:00 PM", "04:30 PM",
]


def identify_user(phone_number: str) -> dict:
    db = SessionLocal()
    try:
        existing = db.query(Appointment).filter(
            Appointment.phone_number == phone_number
        ).first()
        if existing:
            return {
                "status": "existing_user",
                "phone_number": phone_number,
                "name": existing.name,
                "message": f"Welcome back, {existing.name}!",
            }
        return {
            "status": "new_user",
            "phone_number": phone_number,
            "message": "New user identified.",
        }
    finally:
        db.close()


def fetch_slots(date: str) -> dict:
    db = SessionLocal()
    try:
        booked = db.query(Appointment).filter(
            Appointment.date == date,
            Appointment.status == "confirmed",
        ).all()
        booked_times = {a.time for a in booked}
        available = [s for s in AVAILABLE_SLOTS if s not in booked_times]
        return {
            "date": date,
            "available_slots": available,
            "total_available": len(available),
        }
    finally:
        db.close()


def book_appointment(
    phone_number: str,
    name: str,
    date: str,
    time: str,
    reason: str = "General consultation",
) -> dict:
    db = SessionLocal()
    try:
        conflict = db.query(Appointment).filter(
            Appointment.date == date,
            Appointment.time == time,
            Appointment.status == "confirmed",
        ).first()
        if conflict:
            return {
                "status": "error",
                "message": f"The slot {time} on {date} is already booked. Please choose another time.",
            }
        appt = Appointment(
            phone_number=phone_number,
            name=name,
            date=date,
            time=time,
            reason=reason,
        )
        db.add(appt)
        db.commit()
        db.refresh(appt)
        return {
            "status": "confirmed",
            "appointment_id": appt.id,
            "name": name,
            "date": date,
            "time": time,
            "reason": reason,
            "message": f"Appointment confirmed for {name} on {date} at {time}.",
        }
    finally:
        db.close()


def retrieve_appointments(phone_number: str) -> dict:
    db = SessionLocal()
    try:
        appointments = db.query(Appointment).filter(
            Appointment.phone_number == phone_number,
            Appointment.status == "confirmed",
        ).all()
        result = [
            {
                "id": a.id,
                "date": a.date,
                "time": a.time,
                "reason": a.reason,
                "status": a.status,
            }
            for a in appointments
        ]
        return {
            "phone_number": phone_number,
            "appointments": result,
            "count": len(result),
        }
    finally:
        db.close()


def cancel_appointment(appointment_id: int) -> dict:
    db = SessionLocal()
    try:
        appt = db.query(Appointment).filter(Appointment.id == appointment_id).first()
        if not appt:
            return {"status": "error", "message": f"Appointment {appointment_id} not found."}
        if appt.status == "cancelled":
            return {"status": "error", "message": "Appointment is already cancelled."}
        appt.status = "cancelled"
        db.commit()
        return {
            "status": "cancelled",
            "appointment_id": appointment_id,
            "message": f"Appointment on {appt.date} at {appt.time} has been cancelled.",
        }
    finally:
        db.close()


def modify_appointment(appointment_id: int, new_date: str, new_time: str) -> dict:
    db = SessionLocal()
    try:
        appt = db.query(Appointment).filter(Appointment.id == appointment_id).first()
        if not appt:
            return {"status": "error", "message": f"Appointment {appointment_id} not found."}
        conflict = db.query(Appointment).filter(
            Appointment.date == new_date,
            Appointment.time == new_time,
            Appointment.status == "confirmed",
            Appointment.id != appointment_id,
        ).first()
        if conflict:
            return {
                "status": "error",
                "message": f"The slot {new_time} on {new_date} is already booked.",
            }
        old_date, old_time = appt.date, appt.time
        appt.date = new_date
        appt.time = new_time
        db.commit()
        return {
            "status": "modified",
            "appointment_id": appointment_id,
            "old_date": old_date,
            "old_time": old_time,
            "new_date": new_date,
            "new_time": new_time,
            "message": f"Appointment rescheduled from {old_date} {old_time} to {new_date} {new_time}.",
        }
    finally:
        db.close()


def end_conversation(
    room_id: str,
    summary: str,
    appointments: list,
    preferences: str = "",
    phone_number: str = "",
) -> dict:
    db = SessionLocal()
    try:
        record = CallSummary(
            room_id=room_id,
            summary=summary,
            appointments=json.dumps(appointments),
            preferences=preferences,
            phone_number=phone_number,
        )
        db.add(record)
        db.commit()
        return {
            "status": "ended",
            "summary": summary,
            "appointments": appointments,
            "preferences": preferences,
            "timestamp": datetime.utcnow().isoformat(),
        }
    finally:
        db.close()
