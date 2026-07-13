def build_prompt(
    user_message: str,
    retrieved_chunks: list[Chunk],
    history: list[Message],  # últimos N turnos, no toda la conversación 
) -> list[dict]:
    # arma la lista de mensajes para Groq: 
    # system prompt + historial acotado + contexto recuperado + pregunta
    return

async def generate_response(messages: list[dict]) -> str:
    # llamada a Groq, sin streaming, devuelve el texto completo
    return