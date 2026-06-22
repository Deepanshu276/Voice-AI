import asyncio
import json
import logging
import os

from dotenv import load_dotenv
from livekit.agents import (
    Agent,
    AgentSession,
    AutoSubscribe,
    JobContext,
    JobProcess,
    WorkerOptions,
    cli,
    function_tool,
)
from livekit.plugins import deepgram, openai

import tools as appointment_tools
from prompts import SYSTEM_PROMPT

load_dotenv()
logger = logging.getLogger("voice-agent")


class HealthcareAgent(Agent):
    def __init__(self, ctx: JobContext):
        super().__init__(instructions=SYSTEM_PROMPT)
        self._ctx = ctx
        self._room_id = ctx.room.name

    async def _send(self, payload: dict):
        try:
            await self._ctx.room.local_participant.publish_data(
                json.dumps(payload).encode(),
                reliable=True,
            )
        except Exception as e:
            logger.error(f"Data send error: {e}")

    @function_tool
    async def identify_user(self, phone_number: str) -> str:
        """Identify the user by their phone number. Always call this first."""
        await self._send({"type": "tool_call", "tool": "identify_user", "status": "calling"})
        result = appointment_tools.identify_user(phone_number)
        await self._send({"type": "tool_call", "tool": "identify_user", "status": "done", "result": result})
        return json.dumps(result)

    @function_tool
    async def fetch_slots(self, date: str) -> str:
        """Fetch available appointment slots for a given date. Date must be in YYYY-MM-DD format."""
        await self._send({"type": "tool_call", "tool": "fetch_slots", "status": "calling"})
        result = appointment_tools.fetch_slots(date)
        await self._send({"type": "tool_call", "tool": "fetch_slots", "status": "done", "result": result})
        return json.dumps(result)

    @function_tool
    async def book_appointment(
        self,
        phone_number: str,
        name: str,
        date: str,
        time: str,
        reason: str = "General consultation",
    ) -> str:
        """Book an appointment for the patient. Date in YYYY-MM-DD, time like '10:00 AM'."""
        await self._send({"type": "tool_call", "tool": "book_appointment", "status": "calling"})
        result = appointment_tools.book_appointment(phone_number, name, date, time, reason)
        status = "done" if result.get("status") == "confirmed" else "error"
        await self._send({"type": "tool_call", "tool": "book_appointment", "status": status, "result": result})
        return json.dumps(result)

    @function_tool
    async def retrieve_appointments(self, phone_number: str) -> str:
        """Get all confirmed appointments for a patient by their phone number."""
        await self._send({"type": "tool_call", "tool": "retrieve_appointments", "status": "calling"})
        result = appointment_tools.retrieve_appointments(phone_number)
        await self._send({"type": "tool_call", "tool": "retrieve_appointments", "status": "done", "result": result})
        return json.dumps(result)

    @function_tool
    async def cancel_appointment(self, appointment_id: int) -> str:
        """Cancel an existing appointment by its ID."""
        await self._send({"type": "tool_call", "tool": "cancel_appointment", "status": "calling"})
        result = appointment_tools.cancel_appointment(appointment_id)
        await self._send({"type": "tool_call", "tool": "cancel_appointment", "status": "done", "result": result})
        return json.dumps(result)

    @function_tool
    async def modify_appointment(self, appointment_id: int, new_date: str, new_time: str) -> str:
        """Reschedule an existing appointment to a new date and time."""
        await self._send({"type": "tool_call", "tool": "modify_appointment", "status": "calling"})
        result = appointment_tools.modify_appointment(appointment_id, new_date, new_time)
        await self._send({"type": "tool_call", "tool": "modify_appointment", "status": "done", "result": result})
        return json.dumps(result)

    @function_tool
    async def end_conversation(
        self,
        summary: str,
        appointments: str = "[]",
        preferences: str = "",
        phone_number: str = "",
    ) -> str:
        """End the conversation and generate a call summary. Call when the patient says goodbye or is done."""
        await self._send({"type": "tool_call", "tool": "end_conversation", "status": "calling"})
        appts = json.loads(appointments) if isinstance(appointments, str) else appointments
        result = appointment_tools.end_conversation(self._room_id, summary, appts, preferences, phone_number)
        await self._send({
            "type": "summary",
            "summary": summary,
            "appointments": appts,
            "preferences": preferences,
            "timestamp": result.get("timestamp"),
        })
        await self._send({"type": "tool_call", "tool": "end_conversation", "status": "done", "result": result})
        return json.dumps(result)


async def entrypoint(ctx: JobContext):
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)
    logger.info(f"Agent connected to room: {ctx.room.name}")

    session = AgentSession(
        stt=deepgram.STT(model="nova-2"),
        llm=openai.LLM(
            model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
            base_url="https://api.groq.com/openai/v1",
            api_key=os.environ["GROQ_API_KEY"],
        ),
        tts=deepgram.TTS(model="aura-asteria-en"),
    )

    await session.start(agent=HealthcareAgent(ctx), room=ctx.room)

    await session.generate_reply(
        instructions="Greet the patient. Say: Hello, I'm Aria from Mykare Health. How can I help you today?"
    )


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
