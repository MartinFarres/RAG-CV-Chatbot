def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    """Parsea un frontmatter simple (clave: valor por línea, sin
    listas/anidamiento) delimitado por "---" al inicio del archivo.
    Si no hay frontmatter, devuelve {} y el texto completo.
    """
    if not text.startswith("---"):
        return {}, text.strip()

    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text.strip()

    _, raw_meta, body = parts
    meta: dict[str, str] = {}

    for line in raw_meta.strip().splitlines():
        key, sep, value = line.partition(":")
        if not sep:
            continue
        meta[key.strip()] = value.strip().strip('"').strip("'")

    return meta, body.strip()
