from fastapi import Request
from sentence_transformers import SentenceTransformer
from app.core.db import async_session
from sqlalchemy.ext.asyncio import AsyncSession

def get_embedding_model(request: Request) -> SentenceTransformer:
    return request.app.state.embedding_model

async def get_db_session():
    async with async_session() as session:
        yield session