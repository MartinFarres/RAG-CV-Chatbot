from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models import ChatMessage
from app.services.schemas import Message

DEFAULT_HISTORY_TURNS = 10


async def get_recent_messages(
    session: AsyncSession,
    conversation_id: str,
    limit: int = DEFAULT_HISTORY_TURNS,
) -> list[Message]:
    stmt = (
        select(ChatMessage)
        .where(ChatMessage.conversation_id == conversation_id)
        .order_by(ChatMessage.id.desc())
        .limit(limit)
    )
    result = await session.execute(stmt)
    rows = result.scalars().all()

    return [Message(role=row.role, content=row.content) for row in reversed(rows)]


def add_message(conversation_id: str, role: str, content: str) -> ChatMessage:
    return ChatMessage(conversation_id=conversation_id, role=role, content=content)
