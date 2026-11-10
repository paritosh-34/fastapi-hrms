from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

engine = create_async_engine("sqlite+aiosqlite:///./app.db")

# expire_on_commit=False: objects stay readable after commit(),
# which we need because we return them to FastAPI after committing.
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    """Parent class of every ORM model."""


async def get_db() -> AsyncIterator[AsyncSession]:
    """Yield one session per request, always closed afterwards."""
    async with SessionLocal() as session:
        yield session