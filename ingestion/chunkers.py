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


def _chunk_by_headings(
    text: str, tipo: str, nombre: str, fuente_url: str | None = None
) -> list[IngestChunk]:
    return [
        IngestChunk(content=section, tipo=tipo, nombre=nombre, fuente_url=fuente_url)
        for section in split_by_headings(text)
    ]


def chunk_cv(text: str, nombre: str) -> list[IngestChunk]:
    return _chunk_by_headings(text, tipo="cv", nombre=nombre)


def chunk_readme(text: str, nombre: str, fuente_url: str | None) -> list[IngestChunk]:
    text = text.strip()
    if not text:
        return []

    if len(text) <= SHORT_README_THRESHOLD:
        return [IngestChunk(content=text, tipo="proyecto", nombre=nombre, fuente_url=fuente_url)]

    return _chunk_by_headings(text, tipo="proyecto", nombre=nombre, fuente_url=fuente_url)


def chunk_certificado(text: str, nombre: str, fuente_url: str | None) -> list[IngestChunk]:
    text = text.strip()
    if not text:
        return []
    return [IngestChunk(content=text, tipo="certificado", nombre=nombre, fuente_url=fuente_url)]


def chunk_about_me(text: str, nombre: str) -> list[IngestChunk]:
    # El doc real está armado como preguntas en headings (## / ###), no
    # como párrafos sueltos: partir por heading mantiene cada pregunta
    # (o sub-área, ej. "Seguridad informática" dentro de "por qué este
    # rubro") como una unidad temática autocontenida.
    return _chunk_by_headings(text, tipo="about_me", nombre=nombre)


def chunk_plan_estudio_resumen(text: str, nombre: str) -> list[IngestChunk]:
    return _chunk_by_headings(text, tipo="plan_estudio", nombre=nombre)


def chunk_plan_estudio_materias(rows: list[dict[str, str]]) -> list[IngestChunk]:
    chunks = []

    for row in rows:
        lines = [
            f"Materia: {row['materia']}",
            f"Año de la carrera: {row['anio_carrera']}",
            f"Sección: {row['seccion']}",
            f"Estado: {row['estado']}",
        ]
        if row.get("tipo_aprobacion"):
            lines.append(f"Forma de aprobación: {row['tipo_aprobacion']}")
        if row.get("fecha"):
            lines.append(f"Fecha: {row['fecha']}")
        if row.get("calificacion"):
            lines.append(f"Calificación: {row['calificacion']}")

        chunks.append(
            IngestChunk(
                content="\n".join(lines),
                tipo="plan_estudio",
                nombre=row["materia"],
                fuente_url=None,
            )
        )

    return chunks
