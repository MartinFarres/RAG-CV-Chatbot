from contextlib import asynccontextmanager
from fastapi import FastAPI
from sentence_transformers import SentenceTransformer

from app.routers import chat

@asynccontextmanager
async def lifespan(app: FastAPI):
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

app.include_router(chat.router)


