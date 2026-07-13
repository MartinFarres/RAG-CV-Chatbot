from dataclasses import dataclass

from heading_splitter import split_by_headings

# Por debajo de este umbral, un README se deja como un único chunk en
# vez de partirlo por headings (no tiene sentido trocear un doc corto).
SHORT_README_THRESHOLD = 800


@dataclass
class IngestChunk:
    content: str
    tipo: str
    nombre: str
    fuente_url: str | None


def chunk_cv(text: str, nombre: str) -> list[IngestChunk]:
    return [
        IngestChunk(content=section, tipo="cv", nombre=nombre, fuente_url=None)
        for section in split_by_headings(text)
    ]


def chunk_readme(text: str, nombre: str, fuente_url: str | None) -> list[IngestChunk]:
    text = text.strip()
    if not text:
        return []

    if len(text) <= SHORT_README_THRESHOLD:
        sections = [text]
    else:
        sections = split_by_headings(text)

    return [
        IngestChunk(content=section, tipo="proyecto", nombre=nombre, fuente_url=fuente_url)
        for section in sections
    ]


def chunk_certificado(text: str, nombre: str, fuente_url: str | None) -> list[IngestChunk]:
    text = text.strip()
    if not text:
        return []
    return [IngestChunk(content=text, tipo="certificado", nombre=nombre, fuente_url=fuente_url)]


def chunk_about_me(text: str, nombre: str) -> list[IngestChunk]:
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    return [
        IngestChunk(content=paragraph, tipo="about_me", nombre=nombre, fuente_url=None)
        for paragraph in paragraphs
    ]


def chunk_plan_estudio(materias: list[dict], nombre: str) -> list[IngestChunk]:
    chunks = []

    for materia in materias:
        lines = [f"Materia: {materia['nombre']}"]
        if materia.get("area"):
            lines.append(f"Área: {materia['area']}")
        if materia.get("anio"):
            lines.append(f"Año: {materia['anio']}")
        if materia.get("estado"):
            lines.append(f"Estado: {materia['estado']}")
        if materia.get("nota") is not None:
            lines.append(f"Nota: {materia['nota']}")

        chunks.append(
            IngestChunk(
                content="\n".join(lines),
                tipo="plan_estudio",
                nombre=materia["nombre"],
                fuente_url=None,
            )
        )

    return chunks
