import httpx

from core.config import settings

GITHUB_README_URL = "https://api.github.com/repos/{repo}/readme"


async def fetch_readme(repo: str) -> str | None:
    """Trae el README.md crudo de un repo público vía la API de GitHub.
    Devuelve None si el repo no existe, es privado o falla la request
    (se loguea y se omite en vez de tirar abajo toda la ingesta).
    """
    headers = {"Accept": "application/vnd.github.raw+json"}
    if settings.GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {settings.GITHUB_TOKEN}"

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(GITHUB_README_URL.format(repo=repo), headers=headers)
    except httpx.HTTPError as exc:
        print(f"[ingestion] Error de red trayendo el README de {repo}: {exc}")
        return None

    if response.status_code != 200:
        print(f"[ingestion] No se pudo traer el README de {repo} (HTTP {response.status_code})")
        return None

    return response.text
