import asyncio

from sentence_transformers import SentenceTransformer
from sqlalchemy import delete

import loaders
from chunkers import IngestChunk
from core.config import settings
from core.db import Base, async_session, engine
from core.models import Chunk


async def collect_chunks() -> list[IngestChunk]:
    chunks: list[IngestChunk] = []
    chunks.extend(loaders.load_cv())
    chunks.extend(loaders.load_about_me())
    chunks.extend(loaders.load_certificados())
    chunks.extend(loaders.load_plan_estudio())
    chunks.extend(await loaders.load_proyectos())
    return chunks


def embed_chunks(model: SentenceTransformer, chunks: list[IngestChunk]) -> list[list[float]]:
    return model.encode([chunk.content for chunk in chunks]).tolist()


async def run() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    raw_chunks = await collect_chunks()
    if not raw_chunks:
        print("[ingestion] No se encontró contenido para ingestar, no se toca la tabla chunks.")
        return

    print(f"[ingestion] {len(raw_chunks)} chunks generados, embediendo...")
    model = SentenceTransformer(settings.EMBEDDING_MODEL_NAME, trust_remote_code=True)
    embeddings = embed_chunks(model, raw_chunks)

    # Full re-sync: se borra todo y se reinserta en la misma transacción.
    # El corpus es chico (CV, certificados, unos pocos proyectos) así que
    # rehacerlo entero en cada corrida del CronJob es más simple y
    # confiable que tratar de diffear/upsertear contra el contenido previo.
    async with async_session() as session, session.begin():
        await session.execute(delete(Chunk))
        session.add_all(
            Chunk(
                content=chunk.content,
                embedding=embedding,
                tipo=chunk.tipo,
                nombre=chunk.nombre,
                fuente_url=chunk.fuente_url,
            )
            for chunk, embedding in zip(raw_chunks, embeddings)
        )

    print(f"[ingestion] Listo: {len(raw_chunks)} chunks insertados.")


if __name__ == "__main__":
    asyncio.run(run())
