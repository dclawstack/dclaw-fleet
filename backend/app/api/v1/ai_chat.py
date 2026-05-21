import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.repositories.ai_chat_repo import AIChatMessageRepository, AIChatSessionRepository
from app.schemas.ai_chat import ChatMessageRead, ChatSessionRead, ChatTurn
from app.services.fleet_ai import chat_turn

router = APIRouter()


class ChatRequest(BaseModel):
    session_id: uuid.UUID | None = None
    message: str


@router.post("/chat", response_model=ChatTurn)
async def chat(payload: ChatRequest, db: AsyncSession = Depends(get_db)):
    session, user_msg, assistant_msg, suggestions = await chat_turn(
        db, payload.session_id, payload.message
    )
    return ChatTurn(
        session_id=session.id,
        user_message=ChatMessageRead.model_validate(user_msg),
        assistant_message=ChatMessageRead.model_validate(assistant_msg),
        suggested_actions=suggestions,
    )


@router.get("/sessions/{session_id}", response_model=ChatSessionRead)
async def get_session(session_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    s_repo = AIChatSessionRepository(db)
    session = await s_repo.get_by_id(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    m_repo = AIChatMessageRepository(db)
    messages = await m_repo.for_session(session_id)
    return ChatSessionRead.model_validate({
        "id": session.id,
        "title": session.title,
        "created_at": session.created_at,
        "updated_at": session.updated_at,
        "messages": [ChatMessageRead.model_validate(m) for m in messages],
    })
