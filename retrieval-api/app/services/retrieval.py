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
    top_k: int = 6,
    candidate_pool: int = 30,
) -> list[ChunkResult]:
    query_embedding = (await asyncio.to_thread(model.encode, query)).tolist() # embeddes query

    distance = Chunk.embedding.cosine_distance(query_embedding).label("distance") # chunk simillarity
    stmt = (
        select(Chunk.content, Chunk.tipo, Chunk.nombre, Chunk.fuente_url, distance)
        .order_by(distance)
        .limit(candidate_pool)
    )

    result = await session.execute(stmt)

    candidates = [
        ChunkResult(
            content=row.content,
            tipo=row.tipo,
            nombre=row.nombre,
            fuente_url=row.fuente_url,
            distance=row.distance,
        )
        for row in result
        if row.distance <= 0.7  # prevents weird responses to non scope questions
    ]

    # Dense, keyword-rich sources (ej. el CV) matchean bien contra
    # practicamente cualquier pregunta técnica y pueden ocupar todos los
    # slots del top-k, tapando READMEs de proyectos igual de relevantes.
    # Primero se toma como mucho un chunk por `nombre` (en orden de
    # cercanía), y recién después se completa con los sobrantes.
    seen_nombres: set[str] = set()
    diversified: list[ChunkResult] = []
    leftovers: list[ChunkResult] = []
    for chunk in candidates:
        if chunk.nombre not in seen_nombres:
            seen_nombres.add(chunk.nombre)
            diversified.append(chunk)
        else:
            leftovers.append(chunk)

    return (diversified + leftovers)[:top_k]

