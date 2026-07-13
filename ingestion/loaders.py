import csv
import re
from pathlib import Path

from chunkers import (
    IngestChunk,
    chunk_about_me,
    chunk_certificado,
    chunk_cv,
    chunk_plan_estudio_materias,
    chunk_plan_estudio_resumen,
    chunk_readme,
)
from frontmatter import parse_frontmatter
from github_client import fetch_readme
from heading_splitter import extract_title

SOURCES_DIR = Path(__file__).parent / "sources"

REPOS_LINKS_FILENAME = "repos_links.md"
_GITHUB_URL_RE = re.compile(r"https?://github\.com/([^/\s)]+/[^/\s)]+)")
_REPO_LINE_RE = re.compile(r"\*\*Repositorio:\*\*\s*(\S+)")


def load_cv() -> list[IngestChunk]:
    chunks = []
    for path in sorted((SOURCES_DIR / "cv").glob("*.md")):
        meta, body = parse_frontmatter(path.read_text(encoding="utf-8"))
        nombre = meta.get("nombre", "CV")
        chunks.extend(chunk_cv(body, nombre=nombre))
    return chunks


def load_about_me() -> list[IngestChunk]:
    chunks = []
    for path in sorted((SOURCES_DIR / "about_me").glob("*.md")):
        meta, body = parse_frontmatter(path.read_text(encoding="utf-8"))
        nombre = meta.get("nombre") or extract_title(body) or "About Me"
        chunks.extend(chunk_about_me(body, nombre=nombre))
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
    plan_dir = SOURCES_DIR / "plan_estudio"

    for path in sorted(plan_dir.glob("*.csv")):
        with path.open(encoding="utf-8", newline="") as f:
            rows = list(csv.DictReader(f))
        chunks.extend(chunk_plan_estudio_materias(rows))

    for path in sorted(plan_dir.glob("*.md")):
        meta, body = parse_frontmatter(path.read_text(encoding="utf-8"))
        nombre = meta.get("nombre") or extract_title(body) or path.stem
        chunks.extend(chunk_plan_estudio_resumen(body, nombre=nombre))

    return chunks


def _parse_repo_links(path: Path) -> list[str]:
    repos = []
    for line in path.read_text(encoding="utf-8").splitlines():
        match = _GITHUB_URL_RE.search(line)
        if match:
            repos.append(match.group(1).rstrip("/"))
    return repos


async def load_proyectos() -> list[IngestChunk]:
    """Proyectos públicos con buen README: se listan (una URL de GitHub
    por línea) en sources/readmes/repos_links.md y se traen en vivo vía
    la API de GitHub. El resto de los .md en sources/readmes/ son
    READMEs ya escritos a mano acá (repos privados o sin buen README),
    con el link real citado en una línea "**Repositorio:** <url>"."""
    chunks = []
    readmes_dir = SOURCES_DIR / "readmes"
    links_path = readmes_dir / REPOS_LINKS_FILENAME

    if links_path.exists():
        for repo in _parse_repo_links(links_path):
            text = await fetch_readme(repo)
            if text is None:
                continue
            nombre = repo.split("/")[-1]
            chunks.extend(
                chunk_readme(text, nombre=nombre, fuente_url=f"https://github.com/{repo}")
            )

    for path in sorted(readmes_dir.glob("*.md")):
        if path.name == REPOS_LINKS_FILENAME:
            continue

        text = path.read_text(encoding="utf-8")
        nombre = extract_title(text) or path.stem
        match = _REPO_LINE_RE.search(text)
        fuente_url = match.group(1) if match else None
        chunks.extend(chunk_readme(text, nombre=nombre, fuente_url=fuente_url))

    return chunks
