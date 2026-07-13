import re

_HEADING_RE = re.compile(r"^(#{1,6})[ \t]+.*$", re.MULTILINE)
_H1_RE = re.compile(r"^#[ \t]+(.+)$", re.MULTILINE)


def extract_title(markdown: str) -> str | None:
    """Devuelve el texto del primer heading de nivel 1 (# Título), o
    None si no hay ninguno."""
    match = _H1_RE.search(markdown)
    return match.group(1).strip() if match else None


def split_by_headings(markdown: str) -> list[str]:
    """Parte un markdown en un bloque por heading (cualquier nivel),
    cada uno con su heading + contenido hasta el próximo heading.

    Un heading sin cuerpo (ej: "## Experiencia" seguido directo de un
    "### Proyecto A") se funde con el siguiente bloque en vez de quedar
    como un chunk vacío.
    """
    matches = list(_HEADING_RE.finditer(markdown))
    if not matches:
        text = markdown.strip()
        return [text] if text else []

    raw_blocks = []
    preamble = markdown[: matches[0].start()].strip()
    if preamble:
        raw_blocks.append(preamble)

    for i, match in enumerate(matches):
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(markdown)
        raw_blocks.append(markdown[start:end].strip())

    blocks: list[str] = []
    pending_heading: str | None = None

    for block in raw_blocks:
        _, _, body = block.partition("\n")
        if not body.strip():
            pending_heading = block if pending_heading is None else f"{pending_heading}\n{block}"
            continue

        if pending_heading:
            block = f"{pending_heading}\n{block}"
            pending_heading = None

        blocks.append(block)

    if pending_heading:
        blocks.append(pending_heading)

    return blocks
