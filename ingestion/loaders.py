import json
from pathlib import Path

from chunkers import (
    IngestChunk,
    chunk_about_me,
    chunk_certificado,
    chunk_cv,
    chunk_plan_estudio,
    chunk_readme,
)
from projects import PROJECTS
from frontmatter import parse_frontmatter
from github_client import fetch_readme

SOURCES_DIR = Path(__file__).parent / "sources"


def load_cv() -> list[IngestChunk]:
    chunks = []
    for path in sorted((SOURCES_DIR / "cv").glob("*.md")):
        chunks.extend(chunk_cv(path.read_text(encoding="utf-8"), nombre="CV"))
    return chunks


def load_about_me() -> list[IngestChunk]:
    chunks = []
    for path in sorted((SOURCES_DIR / "about_me").glob("*.md")):
        chunks.extend(chunk_about_me(path.read_text(encoding="utf-8"), nombre="About Me"))
    return chunks


def load_certificados() -> list[IngestChunk]:
    chunks = []
    for path in sorted((SOURCES_DIR / "certificados").glob("*.md")):
        meta, body = parse_frontmatter(path.read_text(encoding="utf-8"))
        nombre = meta.get("nombre", path.stem)
        fuente_url = meta.get("fuente_url")
        chunks.extend(chunk_certificado(body, nombre=nombre, fuente_url=fuente_url))
    return chunks


def load_plan_estudio() -> list[IngestChunk]:
    chunks = []
    for path in sorted((SOURCES_DIR / "plan_estudio").glob("*.json")):
        materias = json.loads(path.read_text(encoding="utf-8"))
        chunks.extend(chunk_plan_estudio(materias, nombre=path.stem))
    return chunks


async def load_proyectos() -> list[IngestChunk]:
    chunks = []

    for project in PROJECTS:
        nombre = project["nombre"]

        if "github" in project:
            repo = project["github"]
            text = await fetch_readme(repo)
            if text is None:
                continue
            fuente_url = project.get("fuente_url", f"https://github.com/{repo}")
        else:
            local_path = SOURCES_DIR / project["local_file"]
            if not local_path.exists():
                print(f"[ingestion] Falta el archivo local {local_path}, se omite '{nombre}'.")
                continue
            text = local_path.read_text(encoding="utf-8")
            fuente_url = project.get("fuente_url")

        chunks.extend(chunk_readme(text, nombre=nombre, fuente_url=fuente_url))

    return chunks
