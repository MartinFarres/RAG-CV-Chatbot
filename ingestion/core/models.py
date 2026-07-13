from pgvector.sqlalchemy import Vector
from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from core.db import Base


class Chunk(Base):
    """Debe reflejar exactamente el modelo Chunk de
    retrieval-api/app/core/models.py: ambos servicios leen/escriben la
    misma tabla "chunks" pero ya no comparten código, así que un cambio
    de esquema en uno tiene que replicarse a mano en el otro.
    """

    __tablename__ = "chunks"

    id: Mapped[int] = mapped_column(primary_key=True)
    content: Mapped[str] = mapped_column(Text)
    embedding: Mapped[list[float]] = mapped_column(Vector(1024))  # model dimensions
    tipo: Mapped[str] = mapped_column(String)        # "proyecto" | "cv" | "certificado" | ...
    nombre: Mapped[str] = mapped_column(String)
    fuente_url: Mapped[str] = mapped_column(String, nullable=True)
