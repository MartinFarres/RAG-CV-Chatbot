from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sentence_transformers import SentenceTransformer

from app.core.config import settings
from app.core.db import Base, engine
from app.core.models import Chunk, ChatMessage  # noqa: F401 - registran las tablas en Base.metadata
from app.routers import chat

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Debe ser el mismo modelo (y misma dimensión, 1024) que usa
    # ingestion/run.py para embeder los chunks: si difieren, las
    # queries y los chunks quedan en espacios vectoriales distintos.
    app.state.embedding_model = SentenceTransformer(
        settings.EMBEDDING_MODEL_NAME,
        trust_remote_code = True
    )
    print("Model loaded successfully")

    yield
    print("Shutting down model...")
    app.state.embedding_model = None

app = FastAPI(title="retrieval-api", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router)


