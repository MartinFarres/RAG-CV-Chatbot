import asyncio
from sentence_transformers import SentenceTransformer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.models import Chunk
from schemas import ChunkResult

async def retrieve_context(
    query: str,
    model: SentenceTransformer,
    session: AsyncSession,
    top_k: int = 4,
) -> list[ChunkResult]:
    query_embedding = await embed_query(query, model)

    # TODO: armar el select con order_by cosine_distance y limit top_k
    # pista: Chunk.embedding.cosine_distance(query_embedding) te da la distancia
    # como columna calculada, la podés pedir en el select para tenerla en el resultado

    # TODO: ejecutar con session.execute(stmt), iterar resultados

    # TODO: mapear cada fila a ChunkResult


async def embed_query(text: str, model: SentenceTransformer) -> list[float]:
    embedding = await asyncio.to_thread(model.encode, text)
    return embedding.tolist()

async def search_similar_chunks(
    query_embedding: list[float],
    top_k: int = 4,
    tipo_filtro: str | None = None
) -> list[Chunk]:
    # Query SQL a pgVector, operador de distancia coseno, ORDER BY + LIMIT
    # WHERE tipo = tipo_filtro
    return
