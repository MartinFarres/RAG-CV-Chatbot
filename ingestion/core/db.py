from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from core.config import settings


class Base(DeclarativeBase):
    pass


engine = create_async_engine(settings.DATABASE_URL)
async_session = async_sessionmaker(engine)
