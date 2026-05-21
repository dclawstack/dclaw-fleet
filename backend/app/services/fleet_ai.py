"""AI Fleet Copilot — stubbed LLM with rule-based intent routing over live fleet data.

NOTE: This is a deterministic stub. Swap `generate_assistant_reply` to call OpenRouter
or local Ollama once credentials are provisioned; the data-gathering layer below is
already RAG-ready.
"""
import re
import uuid
from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ai_chat import AIChatMessage, AIChatSession
from app.repositories.ai_chat_repo import AIChatMessageRepository, AIChatSessionRepository
from app.repositories.driver_repo import DriverRepository
from app.repositories.maintenance_repo import MaintenanceRepository
from app.repositories.vehicle_repo import VehicleRepository


async def _fleet_snapshot(db: AsyncSession) -> dict:
    v_repo = VehicleRepository(db)
    d_repo = DriverRepository(db)
    m_repo = MaintenanceRepository(db)
    vehicles, vehicle_total = await v_repo.list_all(limit=1000)
    drivers, driver_total = await d_repo.list_all(limit=1000)
    overdue = await m_repo.overdue(date.today())
    return {
        "vehicle_total": vehicle_total,
        "vehicles_active": sum(1 for v in vehicles if v.status == "active"),
        "driver_total": driver_total,
        "drivers_active": sum(1 for d in drivers if d.status == "active"),
        "overdue_maintenance": [
            {"task": t.task_type, "vehicle_id": str(t.vehicle_id), "due": t.due_date and t.due_date.isoformat()}
            for t in overdue
        ],
    }


INTENTS: list[tuple[re.Pattern, str]] = [
    (re.compile(r"\b(how many|count|total)\b.*\b(vehicle|truck|car)s?\b", re.I), "vehicle_count"),
    (re.compile(r"\b(how many|count|total)\b.*\bdrivers?\b", re.I), "driver_count"),
    (re.compile(r"\b(overdue|due|maintenance|service|pm)\b", re.I), "maintenance"),
    (re.compile(r"\b(fuel|mpg|efficien|consumption)\b", re.I), "fuel"),
    (re.compile(r"\b(geofence|boundary|zone)\b", re.I), "geofence"),
    (re.compile(r"\b(hello|hi|hey|help)\b", re.I), "greeting"),
]


def _classify(message: str) -> str:
    for pat, intent in INTENTS:
        if pat.search(message):
            return intent
    return "unknown"


def _render(intent: str, snap: dict) -> tuple[str, list[str]]:
    if intent == "greeting":
        return (
            f"Hi — I'm your Fleet Copilot. You have {snap['vehicle_total']} vehicles and "
            f"{snap['driver_total']} drivers on the books. Ask me about maintenance, fuel, "
            "drivers, vehicles, or geofences.",
            ["List overdue maintenance", "Show low-MPG vehicles", "How many active drivers?"],
        )
    if intent == "vehicle_count":
        return (
            f"You currently have {snap['vehicle_total']} vehicles total, "
            f"{snap['vehicles_active']} of them active.",
            ["Which vehicles are inactive?", "Schedule maintenance"],
        )
    if intent == "driver_count":
        return (
            f"You currently have {snap['driver_total']} drivers, "
            f"{snap['drivers_active']} active.",
            ["List drivers with low safety scores", "Assign driver to vehicle"],
        )
    if intent == "maintenance":
        overdue = snap["overdue_maintenance"]
        if not overdue:
            return (
                "No overdue maintenance tasks — fleet is current.",
                ["Schedule new PM", "Show upcoming tasks"],
            )
        sample = ", ".join(f"{t['task']} (vehicle {t['vehicle_id'][:8]}…)" for t in overdue[:3])
        return (
            f"There are {len(overdue)} overdue maintenance tasks. Top items: {sample}.",
            ["Mark task complete", "Send mechanic alert"],
        )
    if intent == "fuel":
        return (
            "Hit `/api/v1/fuel-logs/vehicles/{vehicle_id}/report` for per-vehicle MPG and anomalies. "
            "I can flag low MPG, suspected fraud (>50% over average), and odometer rollbacks.",
            ["Show vehicles below 8 MPG", "Top fuel spenders this month"],
        )
    if intent == "geofence":
        return (
            "Geofence breaches are evaluated on every GPS ping. "
            "Inclusion fences alert when a vehicle exits; exclusion fences alert when one enters.",
            ["Create geofence", "Recent breach alerts"],
        )
    return (
        "I can help with vehicles, drivers, maintenance, fuel, routes, and geofences. "
        "Try: 'List overdue maintenance' or 'How many active drivers?'",
        ["List overdue maintenance", "How many active drivers?"],
    )


async def chat_turn(
    db: AsyncSession,
    session_id: uuid.UUID | None,
    user_content: str,
) -> tuple[AIChatSession, AIChatMessage, AIChatMessage, list[str]]:
    session_repo = AIChatSessionRepository(db)
    msg_repo = AIChatMessageRepository(db)

    if session_id is None:
        session = AIChatSession(title=user_content[:80] or "Fleet Copilot")
        session = await session_repo.create(session)
    else:
        session = await session_repo.get_by_id(session_id)
        if session is None:
            session = AIChatSession(title=user_content[:80] or "Fleet Copilot")
            session = await session_repo.create(session)

    user_msg = AIChatMessage(session_id=session.id, role="user", content=user_content)
    user_msg = await msg_repo.create(user_msg)

    snapshot = await _fleet_snapshot(db)
    intent = _classify(user_content)
    reply_text, suggestions = _render(intent, snapshot)

    assistant_msg = AIChatMessage(session_id=session.id, role="assistant", content=reply_text)
    assistant_msg = await msg_repo.create(assistant_msg)
    return session, user_msg, assistant_msg, suggestions
