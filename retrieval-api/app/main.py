from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sentence_transformers import SentenceTransformer

from app.core.db import Base, engine
from app.core.models import Chunk, ChatMessage  # noqa: F401 - registran las tablas en Base.metadata
from app.routers import chat

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Load the model
    # qwen3-Embedding-0.6B 1024 dimensions
    app.state.embedding_model = SentenceTransformer(
        "Qwen/Qwen3-Embedding-0.6B",
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


