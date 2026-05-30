"""AI Fleet Copilot — Ollama-backed LLM over live fleet data, with a deterministic
template fallback when Ollama is unconfigured/unreachable (also used by tests)."""
import json
import logging
import re
import uuid
from datetime import date

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.ai_chat import AIChatMessage, AIChatSession
from app.repositories.accident_repo import AccidentRepository
from app.repositories.ai_chat_repo import AIChatMessageRepository, AIChatSessionRepository
from app.repositories.driver_repo import DriverRepository
from app.repositories.expense_repo import ExpenseRepository
from app.repositories.maintenance_repo import MaintenanceRepository
from app.repositories.part_repo import PartRepository
from app.repositories.permit_repo import PermitRepository
from app.repositories.vehicle_repo import VehicleRepository


async def _fleet_snapshot(db: AsyncSession) -> dict:
    v_repo = VehicleRepository(db)
    d_repo = DriverRepository(db)
    m_repo = MaintenanceRepository(db)
    p_repo = PermitRepository(db)
    e_repo = ExpenseRepository(db)
    a_repo = AccidentRepository(db)
    part_repo = PartRepository(db)

    vehicles, vehicle_total = await v_repo.list_all(limit=1000)
    drivers, driver_total = await d_repo.list_all(limit=1000)
    overdue = await m_repo.overdue(date.today())
    expired_permits = await p_repo.expired()
    expiring_permits = await p_repo.expiring_within(30)
    pending_expenses = await e_repo.pending()
    open_claims = await a_repo.open_claims()
    low_stock = await part_repo.low_stock()

    low_score_drivers = [d for d in drivers if d.safety_score < 70]
    ev_vehicles = [v for v in vehicles if v.fuel_type == "electric"]

    return {
        "vehicle_total": vehicle_total,
        "vehicles_active": sum(1 for v in vehicles if v.status == "active"),
        "ev_count": len(ev_vehicles),
        "driver_total": driver_total,
        "drivers_active": sum(1 for d in drivers if d.status == "active"),
        "low_score_drivers": len(low_score_drivers),
        "overdue_maintenance": [
            {"task": t.task_type, "vehicle_id": str(t.vehicle_id), "due": t.due_date and t.due_date.isoformat()}
            for t in overdue
        ],
        "expired_permits": len(expired_permits),
        "expiring_permits": len(expiring_permits),
        "pending_expenses_count": len(pending_expenses),
        "pending_expenses_amount": sum(float(e.amount) for e in pending_expenses),
        "open_claims_count": len(open_claims),
        "open_claims_amount": sum(float(a.predicted_claim_amount or 0) for a in open_claims),
        "low_stock_parts": len(low_stock),
    }


INTENTS: list[tuple[re.Pattern, str]] = [
    (re.compile(r"\b(how many|count|total)\b.*\b(vehicle|truck|car)s?\b", re.I), "vehicle_count"),
    (re.compile(r"\b(how many|count|total)\b.*\bdrivers?\b", re.I), "driver_count"),
    (re.compile(r"\b(overdue|due|maintenance|service|pm)\b", re.I), "maintenance"),
    (re.compile(r"\b(fuel|mpg|efficien|consumption)\b", re.I), "fuel"),
    (re.compile(r"\b(geofence|boundary|zone)\b", re.I), "geofence"),
    (re.compile(r"\b(safety|coaching|behavior|harsh|speeding|risky)\b", re.I), "safety"),
    (re.compile(r"\b(hos|hours|eld|compliance|inspection|dvir)\b", re.I), "compliance"),
    (re.compile(r"\b(permit|license|expir)\b", re.I), "permits"),
    (re.compile(r"\b(expense|cost|spend|reimburs|fraud)\b", re.I), "expenses"),
    (re.compile(r"\b(assign|dispatch|optimize|route)\b", re.I), "routes"),
    (re.compile(r"\b(ev|electric|charge|charging|range|soc)\b", re.I), "ev"),
    (re.compile(r"\b(accidents?|crash(?:es)?|claims?|incidents?)\b", re.I), "accidents"),
    (re.compile(r"\b(parts?|inventory|tires?|brake pads?|stock|reorder)\b", re.I), "parts"),
    (re.compile(r"\b(telematics|obd|devices?|heartbeats?|sensors?)\b", re.I), "telematics"),
    (re.compile(r"\b(dashcams?|cameras?|videos?|distraction|collisions?)\b", re.I), "dashcam"),
    (re.compile(r"\b(predict|predictive|failures?|forecasts?)\b", re.I), "predictive"),
    (re.compile(r"\b(carbon|co2|emissions?|footprint|green|eco)\b", re.I), "carbon"),
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
            f"{snap['driver_total']} drivers on the books. Ask about maintenance, fuel, "
            "safety, compliance, expenses, routes, or geofences.",
            ["List overdue maintenance", "Show low-scoring drivers", "Pending expenses?"],
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
    if intent == "safety":
        low = snap["low_score_drivers"]
        if low == 0:
            return (
                "No drivers currently below the 70 safety threshold.",
                ["Show recent driving events", "Coaching tips"],
            )
        return (
            f"{low} driver(s) are under the 70 safety threshold. Pull "
            "`/api/v1/driving-events/drivers/{driver_id}/coaching` for personalized tips.",
            ["List low-score drivers", "Send coaching message"],
        )
    if intent == "compliance":
        return (
            f"{snap['expired_permits']} expired permit(s); {snap['expiring_permits']} expiring in the "
            "next 30 days. HOS status is per-driver — query "
            "`/api/v1/hos-logs/drivers/{driver_id}/status`.",
            ["Show expiring permits", "Today's HOS violations"],
        )
    if intent == "permits":
        return (
            f"{snap['expired_permits']} expired and {snap['expiring_permits']} expiring within 30 days. "
            "Renew via `/api/v1/permits/{id}`.",
            ["List expired permits", "Renew highest-priority permit"],
        )
    if intent == "expenses":
        return (
            f"{snap['pending_expenses_count']} expense(s) pending approval totaling "
            f"${snap['pending_expenses_amount']:,.2f}. I'll auto-categorize on submit and "
            "flag duplicates/oversized amounts.",
            ["Approve pending expenses", "Show flagged expenses"],
        )
    if intent == "routes":
        return (
            "Routes can be optimized with `/api/v1/routes/{id}/optimize`, auto-assigned via "
            "`/api/v1/route-integration/auto-assign`, or planned by the autonomous dispatcher at "
            "`/api/v1/predictive/dispatch/plan` (skips maintenance holds, prefers high-safety drivers).",
            ["Auto-assign all routes", "Run autonomous dispatch"],
        )
    if intent == "ev":
        return (
            f"You have {snap['ev_count']} electric vehicle(s). Per-vehicle range and charge "
            "recommendations are at `/api/v1/charging/vehicles/{id}/range` and `/recommendation`.",
            ["Predict EV range", "Schedule overnight charging"],
        )
    if intent == "accidents":
        if snap["open_claims_count"] == 0:
            return ("No open accident claims — fleet is clear.", ["Log new incident", "Claims history"])
        return (
            f"{snap['open_claims_count']} open claim(s); AI-predicted total ~"
            f"${snap['open_claims_amount']:,.0f}.",
            ["List open claims", "Predict claim amount"],
        )
    if intent == "parts":
        if snap["low_stock_parts"] == 0:
            return ("Parts inventory is healthy — no items below threshold.", ["Add part", "Show usage"])
        return (
            f"{snap['low_stock_parts']} part(s) below reorder threshold. "
            "`/api/v1/parts/reorder-recommendations` will compute order quantities.",
            ["Show reorder recommendations", "Add new part"],
        )
    if intent == "telematics":
        return (
            "Devices are registered at `/api/v1/telematics/devices`. Vendor payloads ingest via "
            "`/heartbeat` and anomalies (missing fields, implausible speed, hot engine) are flagged inline.",
            ["Register device", "Show anomalies"],
        )
    if intent == "dashcam":
        return (
            "Dashcam events stream into `/api/v1/dashcam` — collision, distraction, lane drift, "
            "hard cornering. Severity feeds the driver safety score.",
            ["List collision events", "Top risky drivers"],
        )
    if intent == "predictive":
        return (
            "Predictive maintenance combines odometer, driving events, and dashcam history. "
            "Hit `/api/v1/predictive/maintenance/vehicles/{id}` for component-level risk.",
            ["Show top at-risk vehicles", "Schedule replacements"],
        )
    if intent == "carbon":
        return (
            "Fleet CO2 footprint is derived from fuel logs using EPA factors "
            "(8.887 kg/gal gas, 10.18 kg/gal diesel). Per-vehicle at "
            "`/api/v1/predictive/carbon/vehicles/{id}`; fleet total at `/carbon/fleet`.",
            ["Show fleet carbon", "Top emitters"],
        )
    return (
        "I can help with vehicles, drivers, maintenance, fuel, safety, compliance, expenses, "
        "routes, and geofences. Try: 'Show overdue maintenance' or 'How many drivers under 70?'.",
        ["List overdue maintenance", "Show low-scoring drivers"],
    )


log = logging.getLogger(__name__)

_SYSTEM_PROMPT = (
    "You are Fleet Copilot, an assistant for fleet managers. Answer using ONLY "
    "the JSON fleet snapshot the user provides — never invent vehicles, drivers, "
    "or counts. Be concise (1–3 sentences). If the snapshot does not contain the "
    "answer, say so and suggest which API endpoint or page to check. Do not "
    "wrap responses in markdown code blocks."
)


async def _generate_with_ollama(user_content: str, snapshot: dict, history: list[AIChatMessage]) -> str | None:
    """Returns assistant text from Ollama, or None if Ollama is unconfigured/unreachable."""
    if not settings.ollama_url:
        return None

    messages: list[dict] = [{"role": "system", "content": _SYSTEM_PROMPT}]
    for m in history[-6:]:
        messages.append({"role": m.role, "content": m.content})
    messages.append({
        "role": "user",
        "content": f"Fleet snapshot:\n{json.dumps(snapshot, default=str)}\n\nQuestion: {user_content}",
    })

    try:
        async with httpx.AsyncClient(timeout=settings.ollama_timeout_seconds) as http:
            resp = await http.post(
                f"{settings.ollama_url.rstrip('/')}/api/chat",
                json={"model": settings.ollama_model, "messages": messages, "stream": False},
            )
            resp.raise_for_status()
            text = (resp.json().get("message") or {}).get("content", "").strip()
            return text or None
    except Exception as exc:
        log.warning("Ollama call failed, falling back to template: %s", exc)
        return None


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
        history: list[AIChatMessage] = []
    else:
        session = await session_repo.get_by_id(session_id)
        if session is None:
            session = AIChatSession(title=user_content[:80] or "Fleet Copilot")
            session = await session_repo.create(session)
            history = []
        else:
            history = await msg_repo.for_session(session.id)

    user_msg = AIChatMessage(session_id=session.id, role="user", content=user_content)
    user_msg = await msg_repo.create(user_msg)

    snapshot = await _fleet_snapshot(db)
    intent = _classify(user_content)
    template_text, suggestions = _render(intent, snapshot)

    llm_text = await _generate_with_ollama(user_content, snapshot, history)
    reply_text = llm_text or template_text

    assistant_msg = AIChatMessage(session_id=session.id, role="assistant", content=reply_text)
    assistant_msg = await msg_repo.create(assistant_msg)
    return session, user_msg, assistant_msg, suggestions
