from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer

from app.core.dependencies import get_embedding_model
from app.services.generation import generate_response
from app.services.retrieval import retrieve_context

router = APIRouter()


class ChatRequest(BaseModel):
    message: str
    conversation_id: str | None = None


class ChatResponse(BaseModel):
    response: str
    conversation_id: str | None = None


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    model: SentenceTransformer = Depends(get_embedding_model),
) -> ChatResponse:
    context = await retrieve_context(request.message, model=model)
    answer = await generate_response(request.message, context)
    return ChatResponse(response=answer, conversation_id=request.conversation_id)