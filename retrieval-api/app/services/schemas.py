from pydantic import BaseModel

class ChunkResult(BaseModel):
    content: str
    tipo: str
    nombre: str
    fuente_url: str | None
    distance: float