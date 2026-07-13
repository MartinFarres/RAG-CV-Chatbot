import asyncio
from sentence_transformers import SentenceTransformer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.models import Chunk
from app.services.schemas import ChunkResult

async def retrieve_context(
    query: str,
    model: SentenceTransformer,
    session: AsyncSession,
    top_k: int = 4,
) -> list[ChunkResult]:
    query_embedding = (await asyncio.to_thread(model.encode, query)).tolist() # embeddes query

    distance = Chunk.embedding.cosine_distance(query_embedding).label("distance") # chunk simillarity
    stmt = (
        select(Chunk.content, Chunk.tipo, Chunk.nombre, Chunk.fuente_url, distance)
        .order_by(distance)
        .limit(top_k)
    )

    result = await session.execute(stmt)

    result = [
        ChunkResult(
            content=row.content,
            tipo=row.tipo,
            nombre=row.nombre,
            fuente_url=row.fuente_url,
            distance=row.distance,
        )
        for row in result
    ]

    return [r for r in result if r.distance <= 0.4] # prevents weird responses to non scope questions



