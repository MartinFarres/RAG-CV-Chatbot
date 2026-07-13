import uuid

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db_session, get_embedding_model
from app.services.generation import build_prompt, generate_response
from app.services.history import add_message, get_recent_messages
from app.services.retrieval import retrieve_context

router = APIRouter()


class ChatRequest(BaseModel):
    message: str
    conversation_id: str | None = None


class ChatResponse(BaseModel):
    response: str
    conversation_id: str


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    model: SentenceTransformer = Depends(get_embedding_model),
    session: AsyncSession = Depends(get_db_session),
) -> ChatResponse:
    conversation_id = request.conversation_id or str(uuid.uuid4())

    history = await get_recent_messages(session, conversation_id)
    chunks = await retrieve_context(request.message, model=model, session=session)
    messages = build_prompt(request.message, chunks, history=history)
    answer = await generate_response(messages)

    session.add(add_message(conversation_id, "user", request.message))
    session.add(add_message(conversation_id, "assistant", answer))
    await session.commit()

    return ChatResponse(response=answer, conversation_id=conversation_id)