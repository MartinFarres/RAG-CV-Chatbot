from db import Base
from pgvector.sqlalchemy import Vector
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Text, DateTime

class Chunk(Base):
    __tablename__ = "chunks"

    id: Mapped[int] = mapped_column(primary_key=True)
    content: Mapped[str] = mapped_column(Text)
    embedding: Mapped[list[float]] = mapped_column(Vector(1024))  # model dimensions
    tipo: Mapped[str] = mapped_column(String)        # "proyecto" | "cv" | "certificado" | ...
    nombre: Mapped[str] = mapped_column(String)
    fuente_url: Mapped[str] = mapped_column(String, nullable=True)

# class messages(Base):
#     __tablename__ = "messages"
#     id: Mapped[int] = mapped_column(primary_key=True)
#     conversation_id: Mapped[int] = mapped_column(Text)
#     role: 'user' | 'assistant'
#     content: str
#     created_at: DateTime