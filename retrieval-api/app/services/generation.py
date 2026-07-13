from groq import AsyncGroq, RateLimitError

from app.core.config import settings
from app.services.schemas import ChunkResult, Message

client = AsyncGroq(api_key=settings.GROQ_API_KEY)

GROQ_MODEL = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = """Sos un asistente que responde preguntas de reclutadores sobre el perfil profesional de Martín Farrés.

Reglas:
- Respondé ÚNICAMENTE con información presente en el contexto recuperado abajo.
- Si el contexto no tiene información suficiente para responder, decilo explícitamente. No inventes.
- Cuando uses un dato del contexto, mencioná de qué fuente sale (ej: "según su proyecto LoadBalancerAutoScaler-DRL...").
- Mantené un tono profesional pero cercano."""


def build_prompt(
    user_message: str,
    chunks: list[ChunkResult],
    history: list[Message],  # últimos N turnos
) -> list[dict]:
    def _fuente(chunk: ChunkResult) -> str:
        if chunk.fuente_url:
            return f"[Fuente: {chunk.nombre} — {chunk.fuente_url}]"
        return f"[Fuente: {chunk.nombre}]"

    contexto = "\n\n".join(f"{_fuente(chunk)}\n{chunk.content}" for chunk in chunks)

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend({"role": turn.role, "content": turn.content} for turn in history)
    messages.append(
        {"role": "user", "content": f"Contexto:\n{contexto}\n\nPregunta: {user_message}"}
    )

    return messages


async def generate_response(messages: list[dict]) -> str:
    try:
        completion = await client.chat.completions.create(
            model=GROQ_MODEL,
            messages=messages,
        )
    except RateLimitError:
        return "Estoy recibiendo muchas consultas en este momento, probá de nuevo en unos minutos."

    return completion.choices[0].message.content
